import socket
import time

# Set up the sender
HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port to connect to

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        message = "Hello from sender"
        s.sendall(message.encode())
        print("Sent:", message)
        time.sleep(0.5)