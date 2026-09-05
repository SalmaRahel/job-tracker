import json
from ..gemini import call_gemini
from .schemas import CVContent
from ..profile.schemas import ProfileResponse
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader
import os
from weasyprint import HTML
import boto3
from src.config import settings

s3_client = boto3.client("s3")

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

def generate_cv_content(profile: ProfileResponse, jd_text: str) -> CVContent:
    CV_GENERATION_PROMPT = f"""You are a CV content generator. You will receive a candidate's profile data and a job description. Generate tailored CV content in JSON only — no prose, no markdown, no explanation outside the JSON.

RULES:
1. Only use facts already present in the candidate's profile. Never invent skills, experience, projects, education, certifications, or metrics/numbers not given to you.
2. Do NOT remove or hide any project or experience item just because it doesn't match the job description. Include everything from the profile — irrelevant-looking items may still matter to the candidate.
3. For "summary": write 2-4 sentences tailored to the job description, using only real profile facts.
4. For "experience" and "projects" descriptions: return a LIST of short bullet points (2-4 bullets per entry), not one paragraph. You may rephrase and reframe emphasis toward the job description's language and priorities — but every fact, technology, and outcome must already exist in the original profile data. Never add quantities, percentages, or user/scale numbers that aren't already stated. Never change an existing number. Each bullet should be one line, concise, professional.
5. Write in the same language as the job description (French or English). If the job description is in French, output all CV text in French. If English, output in English.
6. Keep descriptions concise and professional — the final CV must fit on ONE PAGE. Favor fewer, stronger bullets over long ones.
7. Include a JSON section only if the candidate has real data for it. If a category is empty in the profile, omit that key entirely from your output — never return an empty list.
8. Output valid JSON matching exactly this schema, nothing else:

{{
  "summary": string,
  "experience": [
    {{"title": string, "company": string, "duration": string, "description": [string]}}
  ],
  "education": [
    {{"school": string, "degree": string, "field": string, "year": string}}
  ],
  "projects": [
    {{"name": string, "description": [string], "tech_stack": string, "link": string | null}}
  ],
  "certifications": [
    {{"name": string, "issuer": string, "year": string}}
  ]
}}

Note: "description" is a LIST of bullet strings, not a single string. Every experience and project entry must use this list format.

CANDIDATE PROFILE:
{profile.model_dump_json()}

JOB DESCRIPTION:
{jd_text}

"""
    raw_response = call_gemini(CV_GENERATION_PROMPT, max_retries=1, model_name="gemini-3.5-flash")
    data = json.loads(raw_response)
    try:
        validated = CVContent(**data)
    except ValidationError as e:
        raise ValueError(f"Gemini returned invalid shape: {e}")
    return validated


def render_cv_html(profile: ProfileResponse, cv_content: CVContent, palette_name: str):
    context_dict = {
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "city": profile.city,
        "links": profile.links_json,
        "skills": profile.skills,
        "languages": profile.languages_json,
        "summary": cv_content.summary,
        "experience": cv_content.experience,
        "education": cv_content.education,
        "projects": cv_content.projects,
        "certifications": cv_content.certifications
    }
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    if palette_name is None:
      template = env.get_template("plain_template.html")
    else:
      template = env.get_template("colored_template.html")
      palette_path = os.path.join(TEMPLATES_DIR, "palette.json")
      with open(palette_path) as f:
         palettes = json.load(f)
         selected_palette = palettes[palette_name]
         context_dict.update(selected_palette)

    html = template.render(context_dict)
    return html


def render_cv_pdf(html_string: str) -> bytes:
   pdf_bytes = HTML(string=html_string, base_url=TEMPLATES_DIR).write_pdf()
   return pdf_bytes

    
def upload_cv_to_s3(pdf_bytes: bytes, key: str) -> str:
  s3_client.put_object(
        Bucket=settings.bucket_name,
        Key=key,
        Body=pdf_bytes,
        ContentType="application/pdf"
    )
  return key