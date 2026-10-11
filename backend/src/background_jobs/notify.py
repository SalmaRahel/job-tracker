import json
import logging
from .redis_client import r

logger = logging.getLogger(__name__)


def publish_notification(user_id: int, message: str) -> None:
    try:
        r.publish("notification", json.dumps({"user_id": user_id, "message": message}))
    except Exception:
        logger.exception("Failed to publish notification for user_id=%s", user_id)
