from fastapi import HTTPException, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from ..auth.models import User
from ..jobs.models import Job
from ..auth.dependencies import get_current_user
from .models import CVGeneration
from .schemas import CVDownloadUrlResponse
import os
import boto3
from botocore.config import Config
from src.config import settings
from ..background_jobs.redis_client import r, check_and_set_cooldown

s3_client = boto3.client(
    "s3",
    region_name=os.environ.get("AWS_DEFAULT_REGION", "eu-north-1"),
    config=Config(signature_version="s3v4"),
)

router = APIRouter(prefix="/jobs", tags=["cv_generation"])

@router.post("/{id}/generate-cv", status_code=202)
def generate_cv(id: int, palette_name: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if not check_and_set_cooldown(user.id, id, "generate_cv"):
        raise HTTPException(status_code=429, detail="Please wait before retrying CV generation")

    r.xadd(
        name="jobs_stream",
        fields={
            "job_type": "cv_generation",
            "job_id": str(id),
            "palette_name": palette_name,
        }   
    )

    return {"job_id": id, "status": "queued"}


@router.get("/{id}/download-cv", response_model=CVDownloadUrlResponse)
def get_generated_cv(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    cv_result = db.query(CVGeneration).filter(CVGeneration.job_id == id).first()
    if cv_result is None:
        raise HTTPException(status_code=404, detail="CV not generated yet")

    s3_key = cv_result.s3_key
    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.bucket_name,
            "Key": s3_key,
            "ResponseContentDisposition": "inline",
            "ResponseContentType": "application/pdf",
        },
        ExpiresIn=300,
    )
    return CVDownloadUrlResponse(url=url)