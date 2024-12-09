from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import threading
from fastapi.responses import JSONResponse
import random
from fastapi.middleware.cors import CORSMiddleware
import httpx
from PIL import Image
import io
import cv2
import pathlib
import os

from .safety_monitor import SafetyMonitor
from .utils.hrv_calculations import StressDetector
from .utils.jobs import (
    add_frames_to_queues,
    FixtureStatusQueue,
    DistanceQueue,
    ImageStreamQueue,
)
from .utils.connection_manager import ConnectionManager
from . import rest_api
from .models import populate_db

app = FastAPI()
app.include_router(rest_api.router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


watch_url = "https://jiranek-chochola.cz/die-experts/index.php?limit=15"

CALIBRATING = False
SHOW_OVERLAY = True

# Websocket maanger manager
distance_manager = ConnectionManager()
dummy_manager = ConnectionManager()
fixture_manager = ConnectionManager()
image_manager = ConnectionManager()

# Safety monitor
monitor = SafetyMonitor()

# Hrv stress calculator
stress_detector = StressDetector()

task_pool = None

# Conncurent thread pooi
# Thread for gathering images
monitor_thread = threading.Thread(target=lambda: add_frames_to_queues(monitor))


@app.on_event("startup")
def startup():
    populate_db()
    monitor.start()
    monitor_thread.start()
    asyncio.create_task(generate_image_stream(image_manager, 60))


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
            all_distances = DistanceQueue.all()
            distance = sum(all_distances)/len(all_distances)
            await websocket.send_text(str(distance))
    except WebSocketDisconnect:
        websocket.disconnect()


@app.websocket("/fixtures")
async def fixture_status_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            fixtures = FixtureStatusQueue.get()
            await websocket.send_text(str(fixtures))
    except WebSocketDisconnect:
        websocket.disconnect(websocket)


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
        result = []
        try:
            response = await client.get(watch_url)
            result = response.json()
        except Exception as e:
            print(f"Failed to get the heartrate. Error: {e}")

    if len(result) < 1:
        result = random.randint(60, 120)
    else:
        result = int(result[0]["heartRate"])

    stress_status = stress_detector.add_heart_rate(result)

    try:
        return JSONResponse(
            {
                "heartRate": result,
                "distance": DistanceQueue.get(),
                "stress_status": stress_status,
            }
        )
    except Exception as e:
        return JSONResponse({"error": repr(e)}, 501)


async def toggle_calibration():
    CALIBRATING = not CALIBRATING  # noqa: F823
    return JSONResponse({"calibrating": CALIBRATING})


async def generate_image_stream(manager, hz):
    # Create a NumPy array representing an image (RGB)

    while True:
        # Convert the NumPy array to an image
        rgb_image = ImageStreamQueue.get()
        if rgb_image is None:
            print("No images in the queue yet.")
            await manager.broadcast_bytes(await send_loading_image())
            continue
        
        width = int(rgb_image.shape[0]/2)
        height = int(rgb_image.shape[1]/2)
        rgb_image = cv2.resize(rgb_image, (height, width))
        _, buffer = cv2.imencode(".jpg", rgb_image)

        try:
            # send binary frame data over websocket
            await manager.broadcast_bytes(buffer.tobytes())
        except Exception as e:
            print(e)

        # optional: reduce frame rate for streaming

        # Add a delay to control the frame rate (e.g., 1 frame per second)
        await asyncio.sleep(1 / hz)

async def send_loading_image():
    current_file_path = pathlib.Path(__file__).parent.resolve()
    loading_image_path = os.path.join(current_file_path, "./images/loading.jpg")

    with open(loading_image_path, "rb") as image:
        return image.read()


@app.get("/image")
async def get_image():
    frame = ImageStreamQueue.get()
    if frame is None:
        frame = cv2.imread("./images/loading.jpg", cv2.COLOR_BGR2RGB)
    
    success, encoded_image = cv2.imencode(".jpg", frame)

    image_bytes = io.BytesIO(encoded_image.tobytes())
    return StreamingResponse(image_bytes, media_type="image/jpeg")


@app.websocket("/ws/image")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections and stream frames."""
    await image_manager.connect(websocket)  # Accept the connection
    try:
        await websocket.send_bytes(await send_loading_image())
        while True:
            await asyncio.sleep(10000)
    except WebSocketDisconnect:
        image_manager.disconnect(websocket)



@app.get("/stress_level")
async def get_safety():
    return {"stress_level": stress_detector.get_safetylevel()}


@app.post("/settings/")
def set_image_settings():
    pass
