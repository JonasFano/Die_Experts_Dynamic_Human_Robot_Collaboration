import time
from garminconnect import Garmin

# User credentials for Garmin Connect
USERNAME = "ninalud.01@gmx.de"
PASSWORD = "!N2i0n0a1!"

# Initialize Garmin Client and Login
try:
    api = Garmin(USERNAME, PASSWORD)
    api.login()
except Exception as e:
    print(f"Error logging into Garmin: {e}")
    exit()

def get_hrv_data(date):
    """
    Fetch HRV data for the specified date.
    """
    try:
        print(api.get_activities_fordate(date))
        
        # heart_rate_data = api.get_activity_hr_in_timezones("11998957007")
        # heart_rate_data = api.get_heart_rates(date)
        # if heart_rate_data:
        #     print(f"HRV Data for {date}:")
        #     # print(heart_rate_data)
        # else:
        #     print(f"No HRV data available for {date}.")
    except Exception as e:
        print(f"Error fetching HRV data: {e}")

# Simulate real-time fetching of HRV data
def fetch_hrv_realtime(interval_seconds=30):
    """
    Fetch HRV data every 'interval_seconds' to simulate real-time data.
    """
    print("Starting real-time HRV data fetching (simulated)...\n")

    # Replace with your desired date, or dynamically use today's date
    from datetime import datetime
    today = "2024-10-20" # datetime.today().strftime('%Y-%m-%d')

    while True:
        # Get today's HRV data
        get_hrv_data(today)

        # Wait for the specified interval before fetching again
        time.sleep(interval_seconds)

if __name__ == "__main__":
    # Start real-time HRV data fetching with 10 seconds interval
    fetch_hrv_realtime(10)

