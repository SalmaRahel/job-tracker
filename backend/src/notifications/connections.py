from fastapi import WebSocket

connections: dict[int, list[WebSocket]] = {}

def add_connection(user_id: int, websocket: WebSocket):
    connections.setdefault(user_id, []).append(websocket)

def remove_connection(user_id: int, websocket: WebSocket):
    if user_id not in connections:
        return
    if websocket in connections[user_id]:
        connections[user_id].remove(websocket)
    if not connections[user_id]:
        del connections[user_id]


async def send_notification(user_id: int, message: str) -> None:
    sockets = connections.get(user_id)
    if sockets is None:
        return
    for websocket in sockets:
        await websocket.send_text(message)