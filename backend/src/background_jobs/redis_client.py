import redis
from ..config import settings
r = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=10)

def check_and_set_cooldown(user_id: int, job_id: int, action: str, ttl_seconds: int | None = None) -> bool:
    key = f"cooldown:{action}:{user_id}:{job_id}"
    ttl = settings.action_cooldown_seconds if ttl_seconds is None else ttl_seconds
    return bool(r.set(key, "1", nx=True, ex=ttl))