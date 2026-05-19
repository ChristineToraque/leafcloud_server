import time
import statistics
import json
import os

def calculate_ec_k_value(avg_ec_voltage: float, target_ec: float = 1.413) -> float:
    """
    Calculates the EC calibration multiplier (K-value).
    
    This is a standalone extraction of the logic used in data_gathering.py.
    It divides the known target EC concentration by the median voltage 
    read from the sensor.
    
    Args:
        avg_ec_voltage (float): The median voltage measured from the EC sensor.
        target_ec (float): The target standard EC value in mS/cm (default is 1.413).
        
    Returns:
        float: The calculated K-value, or None if the probe is likely disconnected.
    """
    # Safety check: ensure voltage is high enough to avoid division by zero 
    # or calibrating against a disconnected probe.
    if avg_ec_voltage > 0.1:
        return target_ec / avg_ec_voltage
    
    return None

def get_stable_ec_voltage(ec_channel) -> float:
    """
    Reads multiple samples from the EC sensor and returns the median 
    voltage to filter out electrical noise.
    
    This is a standalone extraction of the sampling logic used in data_gathering.py.
    
    Args:
        ec_channel: The Adafruit analog input channel (e.g., AnalogIn(ads, 0)).
        
    Returns:
        float: The stable median voltage.
    """
    ec_readings = []
    
    # Take 20 samples to filter out noise
    for _ in range(20):
        ec_readings.append(ec_channel.voltage)
        time.sleep(0.02)
        
    # Use median to ignore electrical spikes
    return statistics.median(ec_readings)


if __name__ == "__main__":
    print("🔌 Initializing Hardware on Raspberry Pi...")
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

    # 1. Initialize the I2C communication pins on the Raspberry Pi
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # 2. Initialize the ADS1115 ADC chip that the sensors are plugged into
    ads = ADS.ADS1115(i2c)
    
    # 3. Create the analog channel object pointing to pin A0 (where the EC sensor is connected)
    ec_channel = AnalogIn(ads, 0)
    
    print("✅ Hardware initialized. Reading stable voltage...")
    
    # 4. Get a stable reading using the median filter function
    stable_voltage = get_stable_ec_voltage(ec_channel)
    print(f"📊 Stable Voltage Read: {stable_voltage:.4f}V")
    
    # 5. Calculate K-Value (Assuming dipped in 1.413 mS/cm calibration solution)
    print("⚙️ Calculating K-Value for 1.413 mS/cm target...")
    k_value = calculate_ec_k_value(stable_voltage)
    
    if k_value:
        print(f"💎 Success! Your new EC_K_VALUE is: {k_value:.4f}")
        
        # 6. Save to calibration file
        cal_file = "calibration_config.json"
        cal_data = {}
        
        # Load existing data first so we don't overwrite pH calibration points!
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