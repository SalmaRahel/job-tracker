from fastapi import APIRouter, Depends, HTTPException, status # The main FastAPI class — creates the app object
from .models import  User   # ORM model (Internship) + enum (ApplicationStatus)
from ..database import get_db                  # Session factory — call SessionLocal() to get a DB session
from .schemas import UserCreate, UserResponse, UserLogin     
from sqlalchemy.orm import Session
from .security import hash_password, verify_password 
from datetime import datetime, timedelta, timezone
from src.config import settings
from .dependencies import ALGORITHM
import jwt
import logging



router = APIRouter(tags=["auth"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session=Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first() 
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account already exist")
    new_user = User(
        email = user.email,
        hashed_password = hash_password(user.password)   
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login_user(user: UserLogin, db: Session=Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing is None:
        logger.warning(f"user not found for the email {user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    
    is_password_correct = verify_password(user.password, existing.hashed_password)
    if is_password_correct is False:
        logger.warning(f"wrong password for user id: [{existing.id}]")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    logger.info(f"user id[{existing.id}] logged in")
    payload = { 
        "sub": str(existing.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(settings.access_token_expire_minutes))
    }

    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
