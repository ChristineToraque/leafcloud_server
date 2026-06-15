import os
import sys
import time
import json
import fcntl
import subprocess
import threading
import signal
import requests
from typing import Dict
from discovery_client import discover_server

PAYLOAD_FILE = "payload.json"
# Dictionary of long-running background daemon scripts
BACKGROUND_SERVICES = {
    "EC Reader": "ec_reader.py",
    "pH Reader": "ph_reader.py",
    "Temp Reader": "temp_reader.py",
    "Camera Capture": "camera_capture.py",
    "EC Calibration": "ec_calibration.py",
    "pH Calibration": "ph_calibration.py"
}

class Orchestrator:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.threads = []
        self.running = True
        self.server_url = None
        self.last_upload_time = 0
        self.suspended_services = set()

    def discover_leafcloud_server(self) -> str:
        """Finds the server URL via Zeroconf or falls back to localhost."""
        print("🔍 [Orchestrator] Searching for LeafCloud Server...")
        url = discover_server(timeout=15)
        if url:
            print(f"📡 [Orchestrator] Found Server at: {url}")
            return url
        print("⚠️ [Orchestrator] Discovery failed. Defaulting to http://localhost:8000")
        return "http://localhost:8000"

    def log_streamer(self, name: str, proc: subprocess.Popen):
        """Pipes stdout/stderr from a subprocess and prefixes it with the process name."""
        try:
            for line in iter(proc.stdout.readline, ''):
                if not self.running:
                    break
                if line:
                    print(f"[{name}] {line.strip()}")
        except Exception:
            pass

    def start_service(self, name: str, script_name: str):
        """Starts a background Python script and launches a monitoring/logging thread."""
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        print(f"🚀 [Orchestrator] Starting background service: {name} ({script_name})...")
        
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes[name] = proc
        
        t = threading.Thread(target=self.log_streamer, args=(name, proc), daemon=True)
        t.start()
        self.threads.append(t)

    def stop_all_services(self):
        """Gracefully terminates all running background processes."""
        self.running = False
        print("\n🛑 [Orchestrator] Stopping all background services...")
        for name, proc in self.processes.items():
            if proc.poll() is None:
                print(f"⌛ [Orchestrator] Terminating {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("✅ [Orchestrator] Cleanup finished.")


    def resolve_tank_config(self) -> tuple:
        """
        Resolves the target tank ID and upload interval (in seconds)
        based on server configurations (highest priority) and local_settings.json.
        Returns a tuple of (tank_id, upload_interval_seconds).
        """
        server_tank_id = None
        server_interval = None

        # 1. Try to fetch from server first (highest priority)
        url = f"{self.server_url}/api/v1/tank-configs/"
        try:
            response = requests.get(url, timeout=5.0)
            if response.status_code == 200:
                configs = response.json()
                # Find local setting if any
                local_tank_id = None
                settings_file = os.path.join(os.path.dirname(__file__), "local_settings.json")
                if os.path.exists(settings_file):
                    try:
                        with open(settings_file, "r") as f:
                            settings = json.load(f)
                            local_tank_id = settings.get("tank_id")
                    except Exception:
                        pass
                
                target_config = None
                if local_tank_id is not None:
                    # Match by local tank_id
                    for config in configs:
                        if config.get("id") == int(local_tank_id):
                            target_config = config
                            break
                
                if target_config is None:
                    # Fall back to finding the active tank
                    for config in configs:
                        if config.get("is_active") is True:
                            target_config = config
                            break
                
                if target_config:
                    server_tank_id = target_config.get("id")
                    server_interval = target_config.get("upload_interval_seconds")
        except Exception as e:
            print(f"⚠️ [Orchestrator] Failed to fetch tank configs from server: {e}")

        # 2. Load from local settings
        local_tank_id = None
        local_interval = None
        settings_file = os.path.join(os.path.dirname(__file__), "local_settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                    local_tank_id = settings.get("tank_id")
                    local_interval = settings.get("upload_interval_seconds")
            except Exception as e:
                print(f"⚠️ [Orchestrator] Error reading local settings: {e}")

        # Resolve tank_id: server (highest) -> local -> fallback 1
        final_tank_id = 1
        if server_tank_id is not None:
            final_tank_id = int(server_tank_id)
        elif local_tank_id is not None:
            final_tank_id = int(local_tank_id)

        # Resolve upload_interval_seconds: server (highest) -> local -> fallback 60
        final_interval = 60
        if server_interval is not None:
            final_interval = int(server_interval)
        elif local_interval is not None:
            final_interval = int(local_interval)

        return final_tank_id, final_interval

    def check_and_upload_payload(self):
        """Safely inspects payload.json and uploads data to the server if all parameters are ready and cooldown has elapsed."""
        if not os.path.exists(PAYLOAD_FILE):
            return

        try:
            with open(PAYLOAD_FILE, "a+") as f:
                # Exclusive lock during read/write
                fcntl.flock(f, fcntl.LOCK_EX)
                
                f.seek(0)
                content = f.read()
                payload = {}
                if content.strip():
                    try:
                        payload = json.loads(content)
                    except Exception as e:
                        print(f"⚠️ [Orchestrator] Error parsing {PAYLOAD_FILE}: {e}")
                        fcntl.flock(f, fcntl.LOCK_UN)
                        return

                # Check if all required sensor values are present
                required_keys = ["ec", "ph", "temperature", "image_path"]
                if all(k in payload for k in required_keys):
                    # Check calibration status from the server (mobile toggle)
                    is_calibrating = False
                    calibrating_sensors = []
                    try:
                        calib_url = f"{self.server_url}/api/v1/calibration/"
                        calib_response = requests.get(calib_url, timeout=3.0)
                        if calib_response.status_code == 200:
                            for cal in calib_response.json():
                                if cal.get("is_calibrating") is True:
                                    is_calibrating = True
                                    calibrating_sensors.append(cal)
                    except Exception as e:
                        # Fall back to False if connection fails
                        pass

                    if is_calibrating:
                        current_time = time.time()
                        if not hasattr(self, "_last_calibration_print") or current_time - self._last_calibration_print >= 10:
                            sensor_names = ", ".join([c.get("sensor_name", "Unknown") for c in calibrating_sensors])
                            print(f"⚠️ [Orchestrator] Calibration mode is active on the server for: {sensor_names}. Suspending uploads...")
                            
                            # Load local calibration config
                            cal_data = {}
                            cal_file = os.path.join(os.path.dirname(__file__), "calibration_config.json")
                            if not os.path.exists(cal_file):
                                cal_file = "calibration_config.json"
                            if os.path.exists(cal_file):
                                try:
                                    with open(cal_file, "r") as f:
                                        cal_data = json.load(f)
                                except Exception:
                                    pass
                            
                            print(f"🔧 [Orchestrator] Local Calibration Config: EC_K_VALUE = {cal_data.get('EC_K_VALUE', 'N/A')}, CAL_POINTS = {cal_data.get('CAL_POINTS', 'N/A')}")
                            print(f"📊 [Orchestrator] Current Payload Readings: Temp = {payload.get('temperature')}°C, EC = {payload.get('ec')} mS/cm, pH = {payload.get('ph')}")
                            self._last_calibration_print = current_time
                        fcntl.flock(f, fcntl.LOCK_UN)
                        return

                    active_tank_id, upload_interval = self.resolve_tank_config()
                    current_time = time.time()
                    
                    # Enforce upload interval cooldown
                    if current_time - self.last_upload_time < upload_interval:
                        # Prevent console spam: only print every 10 seconds during cooldown
                        if not hasattr(self, "_last_cooldown_print") or current_time - self._last_cooldown_print >= 10:
                            remaining = int(upload_interval - (current_time - self.last_upload_time))
                            print(f"⏳ [Orchestrator] Payload populated, but waiting for upload interval cooldown ({remaining}s remaining)...")
                            self._last_cooldown_print = current_time
                        fcntl.flock(f, fcntl.LOCK_UN)
                        return
                    
                    print("📤 [Orchestrator] Cooldown elapsed and payload is ready! Preparing upload...")
                    print(f"🎯 [Orchestrator] Target Tank ID: {active_tank_id}")
                    
                    data = {
                        "tank_id": active_tank_id,
                        "ph": payload["ph"],
                        "ec": payload["ec"],
                        "temp": payload["temperature"]
                    }
                    
                    image_path = payload["image_path"]
                    if not os.path.exists(image_path):
                        print(f"❌ [Orchestrator] Image file not found at {image_path}. Skipping upload.")
                        fcntl.flock(f, fcntl.LOCK_UN)
                        return
                        
                    try:
                        with open(image_path, "rb") as img_file:
                            img_data = img_file.read()
                            
                        files = {
                            "image": (os.path.basename(image_path), img_data, "image/jpeg")
                        }
                        
                        upload_url = f"{self.server_url}/api/v1/iot/upload"
                        response = requests.post(upload_url, data=data, files=files, timeout=10.0)
                        
                        if response.status_code in [200, 201]:
                            print(f"✅ [Orchestrator] Data successfully uploaded! Server Response: {response.json()}")
                            self.last_upload_time = time.time()
                            
                            # Clean the uploaded keys from payload
                            for k in required_keys:
                                payload.pop(k, None)
                            
                            # Write the cleared payload back
                            f.seek(0)
                            f.truncate()
                            json.dump(payload, f, indent=4)
                            print(f"🧹 [Orchestrator] Uploaded values cleared from {PAYLOAD_FILE}")
                        else:
                            print(f"❌ [Orchestrator] Server returned failure status code {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ [Orchestrator] Failed to connect to server for upload: {e}")
                
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"❌ [Orchestrator] Error during payload coordination: {e}")

    def suspend_service(self, name: str):
        """Suspends a service if it is running, and marks it as suspended."""
        if name not in self.suspended_services:
            self.suspended_services.add(name)
        proc = self.processes.get(name)
        if proc and proc.poll() is None:
            print(f"🛑 [Orchestrator] Suspending service '{name}' due to calibration mode...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        # Remove from active processes so it's not checked or respawned
        self.processes.pop(name, None)

    def resume_service(self, name: str):
        """Resumes a suspended service."""
        if name in self.suspended_services:
            self.suspended_services.remove(name)
        if name not in self.processes:
            print(f"🔄 [Orchestrator] Resuming suspended service '{name}'...")
            self.start_service(name, BACKGROUND_SERVICES[name])

    def update_calibration_suspension(self):
        """Fetches active calibration status from the server and suspends/resumes reader services."""
        if not self.server_url:
            return

        is_ph_calibrating = False
        is_ec_calibrating = False

        try:
            calib_url = f"{self.server_url}/api/v1/calibration/"
            response = requests.get(calib_url, timeout=3.0)
            if response.status_code == 200:
                for cal in response.json():
                    if cal.get("is_calibrating") is True:
                        sensor_name = cal.get("sensor_name", "")
                        if "ph" in sensor_name:
                            is_ph_calibrating = True
                        elif "ec" in sensor_name:
                            is_ec_calibrating = True
        except Exception:
            # Silent fallback if offline
            pass

        # Handle pH Reader suspension
        if is_ph_calibrating:
            if "pH Reader" in self.processes:
                self.suspend_service("pH Reader")
        else:
            if "pH Reader" not in self.processes and "pH Reader" in self.suspended_services:
                self.resume_service("pH Reader")

        # Handle EC Reader suspension
        if is_ec_calibrating:
            if "EC Reader" in self.processes:
                self.suspend_service("EC Reader")
        else:
            if "EC Reader" not in self.processes and "EC Reader" in self.suspended_services:
                self.resume_service("EC Reader")

    def monitor_and_loop(self):
        """Main orchestrator monitoring loop."""
        self.server_url = self.discover_leafcloud_server()
        
        # Start all long-running sensor and calibration scripts
        for name, script in BACKGROUND_SERVICES.items():
            self.start_service(name, script)

        last_camera_time = 0
        
        print("\n⭐ [Orchestrator] IoT Orchestration Engine Active. Press Ctrl+C to terminate.")
        print("-" * 80)
        
        try:
            while self.running:
                # Suspend/Resume readers based on active calibration mode
                self.update_calibration_suspension()

                # Check if payload is complete and upload it
                self.check_and_upload_payload()

                # 3. Check health of background services and respawn if dead
                for name, proc in list(self.processes.items()):
                    if name in self.suspended_services:
                        continue
                    if proc.poll() is not None:
                        print(f"⚠️ [Orchestrator] Service '{name}' terminated unexpectedly. Respawning...")
                        self.start_service(name, BACKGROUND_SERVICES[name])

                time.sleep(2)
        except KeyboardInterrupt:
            print("\n👋 [Orchestrator] Shutdown signal received.")
        finally:
            self.stop_all_services()

def signal_handler(signum, frame):
    raise KeyboardInterrupt

if __name__ == "__main__":
    # Register signal handlers for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    orchestrator = Orchestrator()
    orchestrator.monitor_and_loop()
