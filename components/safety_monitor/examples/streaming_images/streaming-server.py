from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import cv2
from contextlib import asynccontextmanager

import pathlib
import os
from safety_monitor.utils.connection_manager import ConnectionManager


manager = ConnectionManager()
cap = None
image_thread = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at startup
    # print("Starting camera")
    while True:
        cap = cv2.VideoCapture(
            0, cv2.CAP_DSHOW
        )  # 0 is the default webcam; use 1, 2, etc., for other cameras
        if cap.isOpened():
            print("Camnera is open")
            break
        else:
            print("Camera not open yet")
    print("Starting images task")
    asyncio.create_task(send_images(cap, manager))
    yield
    # Run on shutdown (if required)
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

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


async def send_loading_image():
    current_file_path = pathlib.Path(__file__).parent.resolve()
    loading_image_path = os.path.join(current_file_path, "../../images/loading.jpg")

    with open(loading_image_path, "rb") as image:
        return image.read()


async def send_images(cap, manager):
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode(".jpg", frame)

        try:
            # Send binary frame data over WebSocket
            await manager.broadcast_bytes(buffer.tobytes())
        except Exception as e:
            print(e)

        # Optional: Reduce frame rate for streaming
        await asyncio.sleep(0.03)  # Approximately 30 fps


@app.websocket("/image")
async def image_endpoint(websocket: WebSocket):
    """WebSocket endpoint."""
    await manager.connect(websocket)
    try:
        await websocket.send_bytes(await send_loading_image())
        while True:  # Loop and sleep forever to keep the connection alive.
            await asyncio.sleep(1000)
    except WebSocketDisconnect:
        print("Disconnection")
        manager.disconnect(websocket)
    except RuntimeError as e:
        print(e)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
