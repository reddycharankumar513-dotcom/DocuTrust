from fastapi import WebSocket


class WebSocketManager:
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def send_json(self, websocket: WebSocket, payload: dict) -> None:
        await websocket.send_json(payload)


manager = WebSocketManager()
