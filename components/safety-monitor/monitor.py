from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from queue import LifoQueue
from safety_minitor import SafetyMonitor
from connection_manager import ConnectionManager
from jobs import add_frames_to_queues
from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading


app = FastAPI()

# Websocket maanger manager
distance_manager = ConnectionManager()
dummy_manager = ConnectionManager()

# Safety monitor
monitor = SafetyMonitor()

task_pool = None

# Conncurent thread pooi

# Queues
DistanceQueue = LifoQueue(0)
ImageStreamQueue = LifoQueue()


class BackgroundTasks(threading.Thread):
    def run(self,*args,**kwargs):
        while True:
            add_frames_to_queues(monitor, DistanceQueue, ImageStreamQueue, ThreadPoolExecutor())

# Thread for gathering images
monitor_thread = threading.Thread(
    target=add_frames_to_queues,
    args=(monitor, DistanceQueue, ImageStreamQueue, ThreadPoolExecutor()),
)

@app.on_event("startup")
def startup():
    monitor.start()
    monitor_thread.start()

#### Api endpoints
@app.websocket("/distance")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint."""
    manager = dummy_manager
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(0.01)
            distance = DistanceQueue.get()
            await manager.broadcast(str(distance))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/dummy")
async def dummy_ws_endpoint(websocket: WebSocket):
    """WebSocket endpoint."""
    manager = dummy_manager
    await manager.connect(websocket)
    try:
        while True:
            asyncio.sleep(1)
            await manager.broadcast("Hello")
    except WebSocketDisconnect:
        manager.disconnect(websocket)