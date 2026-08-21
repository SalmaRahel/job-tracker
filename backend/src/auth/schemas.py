from pydantic import BaseModel, EmailStr


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

class ExperienceItem(BaseModel):
    title: str
    company: str
    duration: str
    description: str

class EducationItem(BaseModel):
    school: str
    degree: str
    field: str
    year: str

class ProjectItem(BaseModel):
    name: str
    description: str
    stack: str | None
    link: str | None

class CertificationItem(BaseModel):
    name: str
    issuer: str
    year: str

class LinkItem(BaseModel):
    label: str
    url: str

class ProfileCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    city: str | None = None
    certifications_json: list[CertificationItem] | None = None
    projects_json: list[ProjectItem] | None = None
    experience_json: list[ExperienceItem] | None = None
    education_json: list[EducationItem] | None = None
    links_json: list[LinkItem] | None = None