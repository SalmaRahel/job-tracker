#security.py
from passlib.context import CryptContext
from src.config import settings
from datetime import datetime, timedelta, timezone
import jwt

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    payload = { 
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(settings.access_token_expire_minutes))
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return token

class InvalidTokenError(Exception):
    pass

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError("Token missing subject")

    return int(user_id)