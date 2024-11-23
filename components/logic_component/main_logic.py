from fetchers import fetchWatchData, fetchSafetyMonitorData
import numpy as np
import threading
import time

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


def start_safety_monitor(speed):
    monitor_thread = threading.Thread(target=fetchSafetyMonitorData, args=(speed,), daemon=True)
    monitor_thread.start()
    return monitor_thread

def fetch_and_process_data(speed):
    while True:
        heartRate = fetchWatchData()
        print("Fetched Watch Data:", heartRate)

        if heartRate and isinstance(heartRate, list) and len(heartRate) > 0:
            try:
                rr_intervals = [float(entry["heartRate"]) for entry in heartRate]
                hrv = calculate_hrv(rr_intervals)
                if hrv:
                    print("Calculated HRV:", hrv)

                speed[0] += 5
                print(f"Speed adjusted by 5 for watch data, New Speed: {speed[0]}")
            except ValueError as e:
                print(f"Error parsing heart rate data: {e}")
        else:
            print("No valid watch data received.")

        time.sleep(1)

if __name__ == "__main__":
    speed = [0] # GPT says it has to be a list to allow modification -> need to test myself
    start_safety_monitor(speed)

    try:
        fetch_and_process_data(speed)
    except KeyboardInterrupt:
        print("\nTerminating the program.")
