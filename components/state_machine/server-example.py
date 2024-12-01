from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
from fastapi.responses import JSONResponse
import random
import httpx

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

@app.get("/data")
async def serve_ui_data():
    return JSONResponse({"heartRate": random.randint(60, 100), "distance": random.randint(60, 100), "stress": random.randint(60, 100)})