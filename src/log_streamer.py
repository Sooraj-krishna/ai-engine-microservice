import asyncio
import queue
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

class LogStreamer:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.router = APIRouter()
        self.router.add_api_websocket_route("/ws/logs", self.websocket_endpoint)
        self.log_queue = queue.Queue()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast_logs(self):
        """Continuously get logs from the queue and broadcast them."""
        while True:
            try:
                message = self.log_queue.get_nowait()
                if self.connections:
                    await asyncio.gather(*(con.send_text(message) for con in self.connections))
            except queue.Empty:
                await asyncio.sleep(0.1) # Wait a bit if queue is empty

    def add_log(self, message: str):
        self.log_queue.put(message)

    async def websocket_endpoint(self, websocket: WebSocket):
        await self.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.disconnect(websocket)

log_streamer = LogStreamer()

# A stream-like object that puts log messages into a thread-safe queue
class QueueLogStream:
    def __init__(self, streamer: LogStreamer):
        self.streamer = streamer

    def write(self, message: str):
        if message.strip():
            self.streamer.add_log(message)

    def flush(self):
        pass
