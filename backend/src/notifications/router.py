from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from .connections import add_connection, remove_connection
from ..auth.security import decode_access_token, InvalidTokenError

router = APIRouter(tags=["notifications"])

TOKEN_TIMEOUT_SECONDS = 10.0

@router.websocket("/ws/notifications")
async def notifications_socket(websocket: WebSocket):
    await websocket.accept()

    try:
        token = await asyncio.wait_for(
            websocket.receive_text(), timeout=TOKEN_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        await websocket.close(code=1008)
        return

    try:
        user_id = decode_access_token(token)
    except InvalidTokenError:
        await websocket.close(code=1008)
        return
    add_connection(user_id, websocket)
    await websocket.send_text(f"authenticated as user {user_id}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        remove_connection(user_id, websocket)

