from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from .models import ApplicationStatus


class JobCreate(BaseModel):
    company_name: str = Field(max_length=100)
    position: str = Field(max_length=150)
    location: str = Field(max_length=50)
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = Field(default=None, max_length=250)
    job_description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED


class JobResponse(BaseModel):
    id: int
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    job_description: Optional[str] = None
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
    company_name: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=150)
    location: Optional[str] = Field(default=None, max_length=50)
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = Field(default=None, max_length=250)
    status: Optional[ApplicationStatus] = None
    job_description: Optional[str] = None