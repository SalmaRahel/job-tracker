import logging
import os
from .redis_client import r
from ..matching.service import run_analysis
from ..cv_generation.service import run_cv_generation
import redis

import src.models  # noqa: F401

logger = logging.getLogger(__name__)

STREAM = "jobs_stream"
GROUP = "workers"
CONSUMER = os.getenv("WORKER_NAME", "worker-1")


def handle(message_id, fields):
    job_type = None
    job_id = None
    try:
        job_type = fields["job_type"]
        job_id = int(fields["job_id"])
        if job_type == "matching":
            run_analysis(job_id)
        elif job_type == "cv_generation":
            palette_name = fields.get("palette_name") or None
            run_cv_generation(job_id, palette_name)
    except Exception:
        logger.exception("Failed to process %s message_id=%s job_id=%s", job_type, message_id, job_id)
    r.xack(STREAM, GROUP, message_id)


def drain(start_id):
    messages = r.xreadgroup(groupname=GROUP, consumername=CONSUMER, streams={STREAM: start_id}, count=1, block=5000)
    handled = 0
    for _stream_name, entries in messages:
        for message_id, fields in entries:
            handle(message_id, fields)
            handled += 1
    return handled


try:
    r.xgroup_create(name=STREAM, groupname=GROUP, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

while drain("0"):
    pass

while True:
    drain(">")
