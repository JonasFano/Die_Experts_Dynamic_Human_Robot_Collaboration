from fastapi import WebSocket
from typing import List


# Keep track of active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print("Peer connected")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        print("Peer disconnected")
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
