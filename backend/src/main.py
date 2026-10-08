import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import src.models  # noqa: F401
from src.config import settings
from src.auth.router import router as auth_router
from src.jobs.router import router as jobs_router
from src.profile.router import router as profile_router
from src.matching.router import router as jd_analysis_router
from src.notifications.router import router as notifications_router
from src.notifications.subscriber import listen_for_notifications  
from src.cv_generation.router import router as cv_generation_router
from src.job_search_query.router import router as job_search_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(listen_for_notifications())  
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(profile_router)
app.include_router(jd_analysis_router)
app.include_router(notifications_router)
app.include_router(cv_generation_router)
app.include_router(job_search_router)