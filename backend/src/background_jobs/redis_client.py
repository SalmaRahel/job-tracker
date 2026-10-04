import redis
from ..config import settings
r = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=10)

def check_and_set_cooldown(user_id: int, job_id: int, action: str) -> bool:
    key = f"cooldown:{action}:{user_id}:{job_id}"
    return bool(r.set(key, "1", nx=True, ex=settings.action_cooldown_seconds))