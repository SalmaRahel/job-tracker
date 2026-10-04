import asyncio
import redis.asyncio as redis
from .connections import send_notification
from ..config import settings
import json
async def listen_for_notifications():
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe("notification")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        payload = json.loads(message["data"])  # parse the JSON string
        user_id = payload["user_id"]
        text = payload["message"]

        await send_notification(user_id, text)