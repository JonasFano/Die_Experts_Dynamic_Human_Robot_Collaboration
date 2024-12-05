from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random
import websockets
import asyncio

app = Flask(__name__)
CORS(app) 

# Store data in memory
data_store = {
    "distance": 1.63,
    "heartRate": 58,
    "stress": 0.5
}

#todo
def calculate_stress(heart_rate):
    random_factor = random.uniform(0.35, 0.65)
    stress = random_factor
    return stress   


# Endpoint to receive distance
# Expects JSON {"distance": float} 
@app.route('/distance', methods=['POST'])
def receive_distance():
    try:
        data = request.json
        distance = data.get('distance')
        if distance is None:
            return jsonify({"error": "Missing 'distance' in request"}), 400
        
        # Store the distance
        data_store['distance'] = distance
        return jsonify({"distance": distance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Function to fetch heartRate from the external server
def fetch_heart_rate_periodically():
    external_url = "https://jiranek-chochola.cz/die-experts/index.php?limit=1"
    while True:
        try:
            response = requests.get(external_url)
            data = response.json()

            if response.status_code == 200:
                heart_rate = data[0]['heartRate']
                if heart_rate is not None:
                    data_store['heartRate'] = int(heart_rate)
                    print(f"Updated heartRate: {heart_rate}")
                    data_store['stress'] = calculate_stress(heart_rate)
                    print(f"Updated stress: {data_store['stress']}")
            else:
                print(f"Failed to fetch heartRate: {response.status_code}")
        except Exception as e:
            print(f"Error fetching heartRate: {e}")

        # Wait for 1 second before the next fetch
        time.sleep(1)


# Endpoint to retrieve stored data
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store), 200



async def test_client():
    uri = "ws://127.0.0.1:8000/distance"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print(f"Server response: {response}")




#threading.Thread(target=fetch_heart_rate_periodically, daemon=True).start()
asyncio.run(test_client())


if __name__ == '__main__':
    app.run(debug=True)
