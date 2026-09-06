from fastapi import HTTPException, APIRouter, Depends
from ..database import get_db    
from sqlalchemy.orm import Session
from ..auth.models import User
from ..jobs.models import Job
from ..auth.dependencies import get_current_user
from .service import generate_cv_content, render_cv_html, render_cv_pdf, upload_cv_to_s3
from .utils import compute_idempotency_key
from .models import CVGeneration
from ..profile.models import Profile
from .schemas import CVDownloadKeyResponse, CVDownloadUrlResponse
import boto3
from src.config import settings

s3_client = boto3.client("s3")



router = APIRouter(prefix="/jobs", tags=["cv_generation"])

@router.post("/{id}/generate-cv", response_model=CVDownloadKeyResponse)
def cv_generation(id: int, palette_name: str, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    
    profile = db.query(Profile).filter(Profile.user_id == job.user_id).first()
    if profile is None or len(profile.skills) < 3:
        raise HTTPException(status_code = 404, detail = "Profile not found")

    key = compute_idempotency_key(id, profile)

    cv_result = db.query(CVGeneration).filter(CVGeneration.key == key).first()
    if cv_result:
        return CVDownloadKeyResponse(s3_key=cv_result.s3_key)

    #generating cv content
    try:
        cv_content = generate_cv_content(profile, job.job_description)
    except ValueError:
        raise HTTPException(status_code=502, detail="CV generation failed — Retry")

    #transforming cv_content to html
    cv_html = render_cv_html(profile, cv_content, palette_name)

    #transformting from html to pdf_yte
    pdf_bytes = render_cv_pdf(cv_html)

    s3_key = upload_cv_to_s3(pdf_bytes, key)

    new_cv = CVGeneration(key=key, job_id=id, s3_key=s3_key)
    db.add(new_cv)
    db.commit()

    return CVDownloadKeyResponse(s3_key=s3_key)

@router.get("/{id}/download-cv", response_model=CVDownloadUrlResponse)
def get_generated_cv(id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    
    cv_result = db.query(CVGeneration).filter(CVGeneration.job_id == id).first()
    if cv_result is None:
        raise HTTPException(status_code = 404, detail = "CV not generated yet")
    
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
    