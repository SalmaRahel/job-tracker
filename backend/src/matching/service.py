import json
from .gemini import call_gemini
from .schemas import JDExtraction
from pydantic import ValidationError

def extract_jd(job_description: str) -> JDExtraction:
    prompt = f"""Extract info from this job description as JSON with these exact keys:
    
    - required_skills (list[string]): normalize casing/naming (e.g. "React.js" -> "React", "postgres" -> "PostgreSQL"). Empty list [] if none found.
    - nice_to_have_skills (list[string]): same normalization rules. Empty list [] if none found.
    - experience_level (string): one of "entry", "mid", "senior", or "unspecified" if not stated.
    - min_years_experience (int or null): null if not explicitly stated.
    - education_requirement (string or null): short normalized form only (e.g. "Bachelor's in Computer Science"), not a full sentence. Null if not stated.
    
    Return raw JSON only, no commentary, no markdown code fences.
    
    Example output:
    {{
        "required_skills": ["Python", "PostgreSQL", "Docker"],
        "nice_to_have_skills": ["Kubernetes"],
        "experience_level": "mid",
        "min_years_experience": 3,
        "education_requirement": "Bachelor's in Computer Science"
    }}
    
    Job description:
    {job_description}"""

    raw_response = call_gemini(prompt, max_retries=2, model_name="gemini-3.5-flash-lite")
    data = json.loads(raw_response)
    try:
        validated = JDExtraction(**data)
    except ValidationError as e:
        raise ValueError(f"Gemini returned invalid shape: {e}")
    return validated

