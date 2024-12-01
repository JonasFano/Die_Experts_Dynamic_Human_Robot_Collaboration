from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import threading
from fastapi.responses import JSONResponse
import random
import httpx

app = FastAPI()


@app.get("/data")
async def serve_ui_data():
    return JSONResponse({"heartRate": random.randint(60, 100), "distance": random.randint(60, 100), "stress": random.randint(60, 100)})