from fastapi import WebSocket, WebSocketDisconnect
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

    async def broadcast_bytes(self, bs: bytearray):
        for connection in self.active_connections:
            try:
                await connection.send_bytes(bs)
            except WebSocketDisconnect:
                self.active_connections.remove(connection)
