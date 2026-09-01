from pydantic import BaseModel, Field


class CVExperienceEntry(BaseModel):
    title: str
    company: str
    duration: str
    description: list[str]


class CVEducationEntry(BaseModel):
    school: str
    degree: str
    field: str
    year: str


class CVProjectEntry(BaseModel):
    name: str
    description: list[str]
    tech_stack: str
    link: str | None = None


class CVCertificationEntry(BaseModel):
    name: str
    issuer: str
    year: str


class CVContent(BaseModel):
    summary: str
    experience: list[CVExperienceEntry] = Field(default_factory=list)
    education: list[CVEducationEntry] = Field(default_factory=list)
    projects: list[CVProjectEntry] = Field(default_factory=list)
    certifications: list[CVCertificationEntry] = Field(default_factory=list)