import json
import logging
import time
from ..gemini import call_gemini
from .schemas import JDExtraction, MatchingOutput
from ..profile.schemas import ProfileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from ..jobs.models import Job
from ..profile.models import Profile
from .models import MatchResult
from .cache import cache_key, read_cached, store_cached
from ..database import SessionLocal
from ..background_jobs.notify import publish_notification

logger = logging.getLogger(__name__)

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

    raw_response = call_gemini(prompt, max_retries=1, model_name="gemini-3.5-flash-lite", temperature=0, thinking_level="MINIMAL")
    data = json.loads(raw_response)
    try:
        validated = JDExtraction(**data)
    except ValidationError as e:
        raise ValueError(f"Gemini returned invalid shape: {e}")
    return validated


def run_matching(jd_extraction_result: JDExtraction, profile: ProfileResponse):
    prompt = f"""You are a job-matching engine. Compare the candidate profile against the job requirements and return a match score.
    SCORING WEIGHTS (strict):
    - Skills match: 70%
    - Experience level: 20%
    - Education: 10%
    Certifications and projects are supporting context only — do not give them their own weighted slice.
    Count a required skill as present when the candidate lists the same skill under a different name or a clear equivalent (for example PostgreSQL counts as SQL).

    CANDIDATE PROFILE:
    {profile.model_dump_json()}
    
    JOB REQUIREMENTS (extracted):
    {jd_extraction_result.model_dump_json()}
    
    OUTPUT INSTRUCTIONS:
    Return ONLY valid JSON, no markdown, no extra text, matching exactly this shape:
    {{
        "score": <int 0-100>,
        "missing_requirements": [<list of plain strings — missing skills AND experience/education gaps>]
    }}"""
    raw_response = call_gemini(prompt, max_retries=1, model_name="gemini-3.5-flash-lite", temperature=0, thinking_level="MINIMAL")
    data = json.loads(raw_response)
    try:
        validated = MatchingOutput(**data)
    except ValidationError as e:
        raise ValueError(f"Gemini returned invalid shape: {e}")
    return validated


def analyze_job(job_id: int, db: Session):
    started = time.perf_counter()
    job = db.query(Job).filter(Job.id == job_id).first()
    if job.job_description is None:
        return

    profile = db.query(Profile).filter(Profile.user_id == job.user_id).first()
    if profile is None or len(profile.skills) < 3:
        return
    profile_data = ProfileResponse.model_validate(profile)
    db_seconds = time.perf_counter() - started

    key = cache_key(job.job_description, profile_data)
    matching_output = read_cached(key)
    extract_seconds = 0.0
    matching_seconds = 0.0
    cache_hit = matching_output is not None

    if cache_hit:
        logger.info("analysis cache hit job_id=%s", job_id)
    else:
        logger.info("analysis cache miss job_id=%s", job_id)
        step = time.perf_counter()
        jd_extracted = extract_jd(job.job_description)
        extract_seconds = time.perf_counter() - step

        step = time.perf_counter()
        matching_output = run_matching(jd_extracted, profile_data)
        matching_seconds = time.perf_counter() - step

    step = time.perf_counter()
    match_result = MatchResult(
        job_id=job.id,
        score=matching_output.score,
        missing_requirements=matching_output.missing_requirements,
    )

    if job.matchresult is not None:
        db.delete(job.matchresult)
        db.commit()

    db.add(match_result)
    db.commit()
    db.refresh(match_result)
    db_seconds += time.perf_counter() - step

    if not cache_hit:
        store_cached(key, matching_output)

    logger.info(
        "analysis timing job_id=%s cache=%s extract=%.2fs matching=%.2fs db=%.2fs total=%.2fs",
        job_id, "hit" if cache_hit else "miss", extract_seconds, matching_seconds, db_seconds, time.perf_counter() - started,
    )
    return match_result


def run_analysis(id: int):
    db = SessionLocal()
    user_id = None
    result = None
    try:
        job = db.query(Job).filter(Job.id == id).first()
        if job is None:
            return
        user_id = job.user_id
        result = analyze_job(id, db)
    except Exception:
        logger.exception("Analysis failed for job_id=%s", id)
    finally:
        db.close()

    if result is not None:
        publish_notification(user_id, f"matching score is ready for user: {user_id}, job_id: {id}")
    elif user_id is not None:
        publish_notification(user_id, f"matching failed for user: {user_id}, job_id: {id}")

