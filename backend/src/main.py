from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.internships.router import router as internships_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(internships_router)