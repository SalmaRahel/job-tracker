#security.py
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

secret_key = settings.secret_key

access_token_expire_minutes = settings.access_token_expire_minutes