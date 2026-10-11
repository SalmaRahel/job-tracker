from fastapi import  Depends, HTTPException, Response, APIRouter # The main FastAPI class — creates the app object
from .models import ApplicationStatus, Job  # ORM model (Job) + enum (ApplicationStatus)
from ..auth.models import User
from ..database import get_db                  # Session factory — call SessionLocal() to get a DB session
from ..auth.dependencies import get_current_user
from .schemas import JobCreate, JobResponse, JobUpdate, JobPage
from sqlalchemy.orm import Session
from typing import Optional
from datetime import  datetime
from sqlalchemy import select, or_, and_
from sqlalchemy import func

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", status_code=201, response_model=JobResponse)
def create_jobs(inter: JobCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    new_job = Job(
        company_name     = inter.company_name,
        position         = inter.position,
        location         = inter.location,
        application_date = inter.application_date,
        deadline         = inter.deadline,
        job_link         = inter.job_link,
        job_description            = inter.job_description,
        status           = inter.status,
        user_id          = user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.get("/", response_model=JobPage)
def get_jobs(db: Session=Depends(get_db), user: User=Depends(get_current_user), last_seen_created_at: Optional[datetime] = None, last_seen_id: Optional[int] = None, search: Optional[str] = None):
    """Returns one page of jobs. On the first page, don't send cursor params."""
    LIMIT=20
    stmt = (
                    select(Job)
                    .where(Job.user_id == user.id)
                    .order_by(Job.created_at.desc(), Job.id.desc())
                    .limit(LIMIT + 1)
        )
    if last_seen_created_at is None and last_seen_id is None:
        pass
    elif last_seen_created_at is not None and last_seen_id is not None:
        stmt = stmt.where(
                or_(
                    Job.created_at < last_seen_created_at,
                    and_(Job.created_at == last_seen_created_at, Job.id < last_seen_id)
                )
            )
    else:
        raise HTTPException(status_code = 400, detail = "both cursor params required together, or neither.")

    if search is not None:
        stmt = stmt.where(Job.search_vector.op("@@")(func.websearch_to_tsquery('english', search)))
    rows = db.execute(stmt).scalars().all()

    has_more = len(rows) > LIMIT

    page = rows[:LIMIT]

    next_cursor = None
    if has_more:
        last = page[-1]
        next_cursor = {"id": last.id, "created_at": last.created_at}

    return JobPage(items=page,has_more=has_more, next_cursor=next_cursor)

@router.get("/{job_id}", response_model=JobResponse)
def get_id_job(job_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, updated_data: JobUpdate, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    updates = updated_data.model_dump(exclude_unset=True)
    # model_dump() is the converstion step that turns it into a plain dict specificlly so it can be loopes over
    for field_name, value in updates.items():
        setattr(job, field_name, value)

    db.commit()
    db.refresh(job)

    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    db.delete(job)
    db.commit()

    return Response(status_code = 204)
