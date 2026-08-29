from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.jobs.router import router as jobs_router
from src.profile.router import router as profile_router
from src.matching.router import router as jd_analysis_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(profile_router)
app.include_router(jd_analysis_router)