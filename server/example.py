import requests
import json
import time
import numpy as np

url = 'https://jiranek-chochola.cz/die-experts/index.php'
rr_intervals = []

def get_latest_data():
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            latest_entry = data[-1]
            print("Newest data:", latest_entry)
            return latest_entry
        else:
            print("No data found.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_hrv(rr_intervals):
    if len(rr_intervals) < 2:
        return None  # Not enough data to calculate HRV
    
    # Calculate differences between successive R-R intervals
    diff_rr = np.diff(rr_intervals)
    
    # Calculate standard deviation of the differences (SDNN)
    sdnn = np.std(rr_intervals)
    
    # Root mean square of successive differences (RMSSD)
    rmssd = np.sqrt(np.mean(diff_rr**2))
    
    return {'SDNN': sdnn, 'RMSSD': rmssd}

while True:
    data = get_latest_data()
    
    if data and 'heartRate' in data:
        try:
            heart_rate = float(data['heartRate'])
            # Calculate R-R interval in milliseconds
            rr_interval = 60000 / heart_rate
            rr_intervals.append(rr_interval)
            
            # Keep only the last 10 intervals for rolling HRV calculation
            if len(rr_intervals) > 10:
                rr_intervals.pop(0)
            
            # Calculate and print HRV
            hrv_metrics = calculate_hrv(rr_intervals)
            if hrv_metrics:
                print(f"HRV Metrics: {hrv_metrics}")
        
        except ValueError:
            print("Invalid heart rate data.")
    
    time.sleep(1)
