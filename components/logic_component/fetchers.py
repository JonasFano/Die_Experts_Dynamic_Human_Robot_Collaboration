import requests
import socket

# returns array of {heartRate: int, timestamp: str}
def fetchWatchData(limit=2, heartRateOnly=True):
    try:
        response = requests.get(f"https://jiranek-chochola.cz/die-experts/index.php?limit={limit}")
        response.raise_for_status()

        data = response.json()
        if heartRateOnly:
            return [{'heartRate': item['heartRate']} for item in data]
        else:
            return [{'heartRate': item['heartRate'], 'timestamp': item['timestamp']} for item in data]

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
def fetchSafetyMonitorData(speed):
    """Run the safety monitor in a separate thread and increase speed for each received socket data."""
    HOST = '127.0.0.1'  # localhost
    PORT = 65432        # Port to listen on

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen()
            print("Safety monitor listening for connections...")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        speed[0] -= 1  # Use list to allow modification in main
                        print(f"Socket data received: {data.decode()}, Speed increased to {speed[0]}")
        except Exception as e:
            print(f"Error in safety monitor: {e}")
        finally:
            print("Safety monitor shutting down.")