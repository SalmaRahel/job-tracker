from pydantic import BaseModel, Field

class JDExtraction(BaseModel):
    required_skills: list[str]
    nice_to_have_skills: list[str]
    experience_level: str
    min_years_experience: int | None = None
    education_requirement: str | None = None

class JDExtractionRequest(BaseModel):
    jd_text: str

class MatchingOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    missing_requirements: list[str]



class MatchResultResponse(BaseModel):
    id: int
    score: int
    missing_requirements: list[str]

    model_config = {"from_attributes": True}
