from jose import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from fastapi.security import OAuth2PasswordBearer

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

ph = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> str:
    try: 
        ph.verify(password, hashed_password)
        return True
    except:
        return False
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt