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

from .safety_monitor import SafetyMonitor
from .utils.hrv_calculations import StressDetector
from .utils.jobs import add_frames_to_queues, FixtureStatusQueue, DistanceQueue, ImageStreamQueue
from .utils.connection_manager import ConnectionManager


app = FastAPI()

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

# Safety monitor
monitor = SafetyMonitor()

# Hrv stress calculator
stress_detector = StressDetector()

task_pool = None

# Conncurent thread pooi
# Thread for gathering images
monitor_thread = threading.Thread(
    target=lambda: add_frames_to_queues(monitor)
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
        result = []
        try:
            response = await client.get(watch_url)
            result = response.json()
        except Exception as e:
            print(f"Failed to get the heartrate. Error: {e}")
    
    if (len(result) < 1):
        result = random.randint(149, 150)
    else:
        result = result[0]["heartRate"] 

    
    stress_status = stress_detector.add_heart_rate(result)

    try:
        return JSONResponse({"heartRate": result, "distance": DistanceQueue.get(), "stress_status": stress_status})
    except Exception as e:
        return JSONResponse({"error": repr(e)}, 501)


async def toggle_calibration():
    CALIBRATING = not CALIBRATING  # noqa: F823
    return JSONResponse({"calibrating": CALIBRATING})


async def generate_image_stream(hz):
    # Create a NumPy array representing an image (RGB)

    while True:
        # Convert the NumPy array to an image
        bgr_image = ImageStreamQueue.get()
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        #image_size = image.size
        #resize_size = (int(image_size[0]/4), int(image_size[1]/4))

        #image = image.resize(resize_size, Image.Resampling.LANCZOS)

        # Save the image to a BytesIO stream
        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_io.seek(0)

        # Yield the image bytes
        yield b"--frame\r\n"
        yield b"Content-Type: image/png\r\n\r\n" + img_io.read() + b"\r\n"

        # Add a delay to control the frame rate (e.g., 1 frame per second)
        await asyncio.sleep(1/hz)


async def generate_frames2(hz):
    while True:
        SCALING = 0.5
        bgr_image = ImageStreamQueue.get()
        (height,width,depth) = bgr_image.shape
        frame = cv2.resize(bgr_image, (int(width/SCALING), int(height/SCALING)))

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)

        # Yield the image bytes
        yield buffer.tobytes()

        # Limit frame rate (e.g., 30 FPS)
        await asyncio.sleep(1 / hz)



@app.get("/image")
async def get_image():
    return StreamingResponse(generate_image_stream(20), media_type="multipart/x-mixed-replace; boundary=frame") 


@app.websocket("/ws/image")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections and stream frames."""
    await websocket.accept()  # Accept the connection
    try:
        async for frame in generate_frames2(60):
            # Send the encoded JPEG frame as binary data
            await websocket.send_bytes(frame)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()

@app.get("/stress_level")
async def get_safety():
    return {"stress_level": stress_detector.get_safetylevel()}