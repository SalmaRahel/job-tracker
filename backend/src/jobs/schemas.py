from pydantic import BaseModel
from typing import Optional
from datetime import date
from .models import ApplicationStatus


class JobCreate(BaseModel):
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    notes: Optional[str] = None



class JobResponse(BaseModel):
    id: int
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    notes: Optional[str] = None
    status: ApplicationStatus

    class Config:
        from_attributes = True


class JobUpdate(BaseModel):
    company_name: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None