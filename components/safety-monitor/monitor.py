from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from queue import LifoQueue
from safety_minitor import SafetyMonitor
from connection_manager import ConnectionManager
from jobs import add_frames_to_queues, FixtureStatusQueue
from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading
from fastapi.responses import JSONResponse
import random
import httpx

app = FastAPI()

watch_url = "https://jiranek-chochola.cz/die-experts/index.php?limit=1"

# Websocket maanger manager
distance_manager = ConnectionManager()
dummy_manager = ConnectionManager()
fixture_manager = ConnectionManager()

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
@app.websocket("/spam/distance")
async def distance_spam_websocket(websocket: WebSocket):
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


#### Api endpoints
@app.websocket("/distance")
async def distance_respond_websocket(websocket: WebSocket):
    """WebSocket endpoint."""
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            distance = DistanceQueue.get()
            await websocket.send_text(str(distance))
    except WebSocketDisconnect:
        websocket.disconnect()

@app.websocket("/fixtures")
async def fixture_status_websocket(websocket: WebSocket):
    manager = fixture_manager
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(0.01)
            fixtures = FixtureStatusQueue.get()
            await manager.broadcast(str(fixtures))
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


@app.get("/data")
async def serve_ui_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(watch_url)
        result = response.json()
        print(result)
    return JSONResponse({"heartRate": result[0]["heartRate"], "distance": DistanceQueue.get(), "stress": random.randint(60, 100)})