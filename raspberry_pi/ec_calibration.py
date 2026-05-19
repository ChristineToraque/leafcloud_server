import time
import statistics
import json
import os
import requests

# ==========================================
# CONFIGURATION
# ==========================================
SERVER_URL = "http://localhost:8000" # Update with your server IP
EC_CALIBRATION_ID = 1  # ID for 'ec_calibration' in the database

def check_calibration_mode() -> bool:
    """Checks the server to see if EC calibration mode is enabled."""
    try:
        response = requests.get(f"{SERVER_URL}/api/v1/calibration/{EC_CALIBRATION_ID}", timeout=5)
        if response.status_code == 200:
            return response.json().get("is_calibrating", False)
    except Exception as e:
        print(f"⚠️ Server connection failed: {e}")
    return False

def reset_calibration_mode():
    """Tells the server that calibration is finished."""
    try:
        requests.patch(
            f"{SERVER_URL}/api/v1/calibration/{EC_CALIBRATION_ID}", 
            json={"is_calibrating": False},
            timeout=5
        )
        print("📡 Server state reset: Calibration Finished.")
    except Exception as e:
        print(f"⚠️ Could not reset server state: {e}")

def calculate_ec_k_value(avg_ec_voltage: float, target_ec: float = 1.413) -> float:
    """
    Calculates the EC calibration multiplier (K-value).
    """
    if avg_ec_voltage > 0.1:
        return target_ec / avg_ec_voltage
    return None

def get_stable_ec_voltage(ec_channel) -> float:
    """
    Reads multiple samples from the EC sensor and returns the median 
    voltage to filter out electrical noise.
    """
    ec_readings = []
    for _ in range(20):
        ec_readings.append(ec_channel.voltage)
        time.sleep(0.02)
    return statistics.median(ec_readings)

if __name__ == "__main__":
    print("📡 Checking calibration signal from server...")
    
    # Polling ensures the RPi and User are in sync
    while not check_calibration_mode():
        print("⏳ Waiting for 'is_calibrating' to be set to TRUE on the dashboard...")
        time.sleep(3)

    print("\n🚀 Signal Received! Starting Hardware Calibration...")

    try:
        print("🔌 Initializing Hardware on Raspberry Pi...")
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ec_channel = AnalogIn(ads, 0)
        
        print("✅ Hardware initialized. Reading stable voltage...")
        stable_voltage = get_stable_ec_voltage(ec_channel)
        print(f"📊 Stable Voltage Read: {stable_voltage:.4f}V")
        
        print("⚙️ Calculating K-Value for 1.413 mS/cm target...")
        k_value = calculate_ec_k_value(stable_voltage)
        
        if k_value:
            print(f"💎 Success! Your new EC_K_VALUE is: {k_value:.4f}")
            cal_file = "calibration_config.json"
            cal_data = {}
            if os.path.exists(cal_file):
                try:
                    with open(cal_file, 'r') as f:
                        cal_data = json.load(f)
                except json.JSONDecodeError:
                    pass
            cal_data["EC_K_VALUE"] = k_value
            with open(cal_file, 'w') as f:
                json.dump(cal_data, f, indent=4)
            print(f"💾 Successfully saved new K-Value to {cal_file}")
        else:
            print("⚠️ Failed: Voltage too low. Is the probe in the solution and connected?")

    except Exception as e:
        print(f"❌ Error during hardware calibration: {e}")
    finally:
        reset_calibration_mode()
