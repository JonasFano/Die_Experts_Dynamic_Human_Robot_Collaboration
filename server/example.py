import requests
import json
import time

url = 'https://jiranek-chochola.cz/die-experts/index.php'

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

while True:
    get_latest_data()
    time.sleep(1)
