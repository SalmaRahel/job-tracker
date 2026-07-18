from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from models import ApplicationStatus


#a schema its the rules for what's allowed to cross the border, in one specific direction 

#with this class: it help pydantic to convert JSON data into a pydantic object /POST
class InternshipCreate(BaseModel):
    company_name: str
    position: str
    location: str
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    notes: Optional[str] = None

#InternshipResponse describes the shape of the JSON that will be sent back. /GET
#It doesn't care what type of object arrives — SQLAlchemy, dictionary, anything.
#from_attributes = True is what gives it the ability to also accept SQLAlchemy objects specifically.
#with the help of this function it help Pyndantic to build a dictionnary from the data inside the SQLAlchemy object 
#Fast api tranform the dictionnary to JSON data

class InternshipResponse(BaseModel):
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


class InternshipUpdate(BaseModel):
    company_name: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    job_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
