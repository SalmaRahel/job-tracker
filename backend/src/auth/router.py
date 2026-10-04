from fastapi import APIRouter, Depends, HTTPException, status 
from .models import  User   
from ..database import get_db                  
from .schemas import UserCreate, UserLogin, TokenResponse  
from sqlalchemy.orm import Session
from .security import hash_password, verify_password, create_access_token
import logging




router = APIRouter(tags=["auth"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=201)
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
    token = create_access_token(new_user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
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
    token = create_access_token(existing.id)
    return TokenResponse(access_token=token)
