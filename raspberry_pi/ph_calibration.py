import time
import statistics
import json
import os

# Default pH Calibration (Multi-point Range) based on your data_gathering.py
DEFAULT_CAL_POINTS = [
    (2.508, 6.86),
    (2.931, 4.01)
]

def get_stable_ph_voltage(ph_channel) -> float:
    """
    Reads multiple samples from the pH sensor and returns the median 
    voltage to filter out electrical noise.
    """
    ph_readings = []
    
    # Take 20 samples to filter out noise
    for _ in range(20):
        ph_readings.append(ph_channel.voltage)
        time.sleep(0.02)
        
    # Use median to ignore electrical spikes
    return statistics.median(ph_readings)

def update_cal_points(voltage: float, target_ph: float, cal_points: list) -> list:
    """
    Updates the specific target pH point in the multi-point array with the new voltage.
    """
    if voltage < 0.1:
        return None  # Voltage too low, likely disconnected
        
    updated_points = []
    point_found = False
    
    for v, p in cal_points:
        if p == target_ph:
            updated_points.append((voltage, target_ph))
            point_found = True
        else:
            updated_points.append((v, p))
            
    # If the user enters a brand new pH point not in the list, add it
    if not point_found:
        updated_points.append((voltage, target_ph))
        
    return updated_points

if __name__ == "__main__":
    print("🔌 Initializing Hardware on Raspberry Pi...")
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

    # 1. Initialize the I2C communication and ADS1115
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    
    # 2. Create the analog channel (Based on your script, pH is on pin A0)
    ph_channel = AnalogIn(ads, 0)
    
    print("✅ Hardware initialized.\n")
    
    # 3. Ask the user which solution they are currently using
    target_input = input("🎯 Enter the target pH solution you are using (e.g., 4.01, 6.86): ")
    try:
        target_ph = float(target_input)
    except ValueError:
        print("❌ Invalid input. Please run again and enter a number like 4.01")
        exit(1)
        
    print("\n⏳ Reading stable voltage... Please keep the probe in the solution.")
    stable_voltage = get_stable_ph_voltage(ph_channel)
    print(f"📊 Stable Voltage Read: {stable_voltage:.4f}V")
    
    # 4. Load existing calibration data (so we don't overwrite EC_K_VALUE or other pH points)
    cal_file = "calibration_config.json"
    cal_data = {}
    cal_points = DEFAULT_CAL_POINTS
    
    if os.path.exists(cal_file):
        try:
            with open(cal_file, 'r') as f:
                cal_data = json.load(f)
                # Convert JSON lists back into Python tuples
                raw_points = cal_data.get("CAL_POINTS", [])
                if raw_points:
                    cal_points = [tuple(p) for p in raw_points]
        except json.JSONDecodeError:
            pass
            
    # 5. Update and Save
    print(f"⚙️ Updating calibration for pH {target_ph}...")
    new_cal_points = update_cal_points(stable_voltage, target_ph, cal_points)
    
    if new_cal_points:
        print(f"\n💎 Success! Current Calibration Points:")
        for v, p in new_cal_points:
            print(f"   pH {p:.2f} -> {v:.4f}V")
            
        cal_data["CAL_POINTS"] = new_cal_points
        with open(cal_file, 'w') as f:
            json.dump(cal_data, f, indent=4)
        print(f"\n💾 Successfully saved new pH points to {cal_file}")
    else:
        print("⚠️ Failed: Voltage too low. Is the probe connected?")