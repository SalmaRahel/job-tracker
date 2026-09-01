import hashlib
from ..profile.schemas import ProfileResponse

def compute_idempotency_key(job_id: int, profile: ProfileResponse) -> str:
    combined = str(job_id) + profile.model_dump_json()
    return hashlib.sha256(combined.encode()).hexdigest()