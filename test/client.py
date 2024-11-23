import socket

HOST = 'server'  # Hostname of the server container (defined in docker-compose.yml)
PORT = 65432     # Must match the server's port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    client_socket.sendall(b"Hello from Client!")
    data = client_socket.recv(1024)

print(f"Received from server: {data.decode()}")
