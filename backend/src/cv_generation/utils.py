import hashlib
from ..profile.schemas import ProfileResponse
from .schemas import CVPalette, CVTemplate

def compute_idempotency_key(job_id: int, profile: ProfileResponse, template: CVTemplate, palette: CVPalette) -> str:
    palette_part = palette.value if template == CVTemplate.COLORED else "-"
    combined = f"{job_id}|{template.value}|{palette_part}|{profile.model_dump_json()}"
    return hashlib.sha256(combined.encode()).hexdigest()
