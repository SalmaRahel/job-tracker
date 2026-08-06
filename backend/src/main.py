from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.jobs.router import router as jobs_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(jobs_router)