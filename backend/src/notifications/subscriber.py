import asyncio
import redis.asyncio as redis
from .connections import send_notification
import json
async def listen_for_notifications():
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe("notification")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        payload = json.loads(message["data"])  # parse the JSON string
        user_id = payload["user_id"]
        text = payload["message"]

        await send_notification(user_id, text)