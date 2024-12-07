from websocket import create_connection
import time

websocket_url = "ws://127.0.0.1:8000/fixtures"  # Replace with your WebSocket URL

while True:
    try:
        # Establish a connection to the WebSocket server
        ws = create_connection(websocket_url)
        print("Connected to WebSocket server")

        # Send a message to the server
        ws.send("Hello, WebSocket!")
        print("Message sent to server")

        # Receive a response from the server
        response = ws.recv()
        print(f"Response from server: {response}")

        # Close the connection
        time.sleep(1)


    except Exception as e:
        print("WebSocket connection closed")
        ws.close()
        print(f"An error occurred: {e}")
