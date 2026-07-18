from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials 
import jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer

load_dotenv()

http_bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials  = Depends(http_bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token error")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentification failed")
    
    user= db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="account deleted after the token was issued")
    return user

    