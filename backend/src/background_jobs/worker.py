from .redis_client import r
from ..matching.service import run_analysis
from ..cv_generation.service import run_cv_generation


r.xgroup_create(name="jobs_stream", groupname="workers", id="0", mkstream=True)

while True:
    messages = r.xreadgroup(
        groupname="workers",
        consumername="worker-1",
        streams={"jobs_stream": ">"},
        count=1,
        block=5000
    )
    for stream_name, entries in messages:
        for message_id, fields in entries:
            job_type = fields["job_type"]
            job_id = int(fields["job_id"])
            if job_type == "matching":
                run_analysis(job_id)
            elif job_type == "cv_generation":
                palette_name = fields.get("palette_name") or None
                run_cv_generation(job_id, palette_name)
            r.xack("jobs_stream", "workers", message_id)