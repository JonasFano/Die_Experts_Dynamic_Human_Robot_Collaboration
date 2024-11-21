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
DistanceQueue = LifoQueue[float](10)
ImageStreamQueue = LifoQueue(10)


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
    try:
        await distance_manager.connect(websocket)
        while True:
            try:
                distance = DistanceQueue.get()
                await distance_manager.broadcast(str(distance))
            except Exception as e:
                print(e)
    except WebSocketDisconnect:
        print("Disconnect!")
        distance_manager.disconnect(websocket)

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