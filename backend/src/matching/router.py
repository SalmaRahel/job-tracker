from fastapi import HTTPException, APIRouter, Depends, BackgroundTasks
from ..database import get_db    
from sqlalchemy.orm import Session
from ..auth.models import User
from ..jobs.models import Job
from ..auth.dependencies import get_current_user
from .service import run_analysis

router = APIRouter(prefix="/jobs", tags=["jd-analysis"])

@router.post("/{id}/analyze")
def jd_analysis(id: int, background_tasks: BackgroundTasks, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    background_tasks.add_task(run_analysis, id)
    return {"message": "Analysis started"}
