from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from queue import LifoQueue
from .safety_minitor import SafetyMonitor
from connection_manager import ConnectionManager
from .utils import add_frames_to_queues
from concurrent.futures import ThreadPoolExecutor
import threading


app = FastAPI()

# Websocket maanger manager
distance_manager = ConnectionManager()

# Safety monitor
monitor = SafetyMonitor()

# Conncurent thread pooi
task_pool = ThreadPoolExecutor(max_workers=10)

# Queues
DistanceQueue = LifoQueue(10)
ImageStreamQueue = LifoQueue(10)


# Thread for gathering images
threading.Thread(
    target=add_frames_to_queues,
    args=(monitor, task_pool, DistanceQueue, ImageStreamQueue),
)


#### Api endpoints
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
