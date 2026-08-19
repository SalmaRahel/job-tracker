from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from .models import ApplicationStatus


class JobCreate(BaseModel):
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    job_description: str


class JobResponse(BaseModel):
    id: int
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    job_description: str
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True

class CursorOut(BaseModel):
    id: int
    created_at: datetime

class JobPage(BaseModel):
    items: list[JobResponse]
    has_more: bool
    next_cursor: Optional[CursorOut] = None




class JobUpdate(BaseModel):
    company_name: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    job_description: Optional[str] = None