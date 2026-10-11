import re
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from pydantic_core import PydanticCustomError
from .email_check import check_email
from typing import Optional

PHONE_PATTERN = re.compile(r"^\+?[0-9\s\-.()]+$")


def clean_phone(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    digits = sum(char in "0123456789" for char in value)
    if not PHONE_PATTERN.match(value) or not 8 <= digits <= 15:
        raise PydanticCustomError("phone", "Enter a valid phone number")
    return value

class SkillCreate(BaseModel):
    name: str

class SkillResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

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
    stack: str | None = None
    link: str | None = None

class CertificationItem(BaseModel):
    name: str
    issuer: str
    year: str

class LinkItem(BaseModel):
    label: str
    url: str

class ProfileCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None
    certifications_json: list[CertificationItem] | None = None
    projects_json: list[ProjectItem] | None = None
    experience_json: list[ExperienceItem] | None = None
    education_json: list[EducationItem] | None = None
    links_json: list[LinkItem] | None = None
    languages_json: list[str] | None = None

    @field_validator("email", mode="before")
    @classmethod
    def check_email_field(cls, value):
        return check_email(value)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value):
        return clean_phone(value)

    @model_validator(mode="after")
    def check_not_empty(self):
        if not (self.experience_json or self.education_json or self.projects_json):
            raise ValueError("provide at least one of experience, education, or projects")
        return self


class ProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None
    certifications_json: list[CertificationItem] | None = None
    projects_json: list[ProjectItem] | None = None
    experience_json: list[ExperienceItem] | None = None
    education_json: list[EducationItem] | None = None
    links_json: list[LinkItem] | None = None
    languages_json: list[str] | None = None
    skills: list[str] = []

    @field_validator("skills", mode="before")
    @classmethod
    def skill_names(cls, value):
        return [getattr(item, "name", item) for item in value or []]

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    certifications_json: Optional[list[CertificationItem]] = None
    projects_json: Optional[list[ProjectItem]] = None
    experience_json: Optional[list[ExperienceItem]] = None
    education_json: Optional[list[EducationItem]] = None
    links_json: Optional[list[LinkItem]] = None
    languages_json: Optional[list[str]] = None

    @field_validator("email", mode="before")
    @classmethod
    def check_email_field(cls, value):
        return check_email(value)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value):
        return clean_phone(value)
