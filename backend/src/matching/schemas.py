from pydantic import BaseModel

class JDExtraction(BaseModel):
    required_skills: list[str]
    nice_to_have_skills: list[str]
    experience_level: str
    min_years_experience: int | None = None
    education_requirement: str | None = None

class JDExtractionRequest(BaseModel):
    jd_text: str