import redis
from ..config import settings
r = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=10)