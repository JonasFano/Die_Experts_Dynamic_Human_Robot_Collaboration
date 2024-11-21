from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from queue import LifoQueue
from .safety_minitor import SafetyMonitor
from connection_manager import ConnectionManager

app = FastAPI()

distance_manager = ConnectionManager()
monitor = SafetyMonitor()


def add_frames_to_queues(m: SafetyMonitor):
    frames = monitor.get_frames()
    DistanceQueue.put(frames)


DistanceQueue = LifoQueue(10)
ImageStreamQueue = LifoQueue(10)


@app.websocket("/distance")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint."""
    await distance_manager.connect(websocket)
    try:
        while True:
            distance = DistanceQueue.get()
            await distance_manager.broadcast(distance)  # Broadcast it
    except WebSocketDisconnect:
        distance_manager.disconnect(websocket)
