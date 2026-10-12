from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CVTemplate(str, Enum):
    PLAIN = "plain"
    COLORED = "colored"


class CVPalette(str, Enum):
    DARK_GRAY_BLUE = "dark_gray_blue"
    FROSTED_MINT = "frosted_mint"
    LIGHT_GRAY = "light_gray"


class GenerateCVRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: CVTemplate = CVTemplate.COLORED
    palette: CVPalette = CVPalette.DARK_GRAY_BLUE


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

class CVDownloadKeyResponse(BaseModel):
    s3_key: str

class CVDownloadUrlResponse(BaseModel):
    url: str