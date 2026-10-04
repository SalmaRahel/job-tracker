#dependencies
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session
from ..database import get_db
from .models import User
from fastapi.security import HTTPBearer
from .security import decode_access_token, InvalidTokenError



http_bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer), db: Session = Depends(get_db)):
    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token error")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="account deleted after the token was issued")
    return user

    