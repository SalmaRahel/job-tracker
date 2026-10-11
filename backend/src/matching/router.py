from fastapi import HTTPException, APIRouter, Depends
from ..database import get_db    
from sqlalchemy.orm import Session
from ..auth.models import User
from ..jobs.models import Job
from ..auth.dependencies import get_current_user
from .schemas import MatchResultResponse

from ..background_jobs.redis_client import r, check_and_set_cooldown

router = APIRouter(prefix="/jobs", tags=["jd-analysis"])

@router.post("/{id}/analyze", status_code=202)
def jd_analysis(id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")

    if not check_and_set_cooldown(user.id, id, "analyze"):
        raise HTTPException(status_code=429, detail="Please wait before retrying analysis")

    r.xadd(
        name="jobs_stream",
        fields={
            "job_type": "matching",
            "job_id": str(id)
        }   
    )
    
    return {"message": "Analysis started"}



@router.get("/{id}/analysis", response_model=MatchResultResponse)
def get_analysis(id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    if job.matchresult is None:
        raise HTTPException(status_code = 404, detail = "Analysis not found")
    return job.matchresult
