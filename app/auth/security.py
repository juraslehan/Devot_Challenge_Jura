from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import User

# using bcrypt as hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# turns users plaintext password into salted hash to store in DB
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

# checks a login attempt, compares plaintext to hash
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# building a signed token
def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire_in = expires_minutes or settings.JWT_EXPIRES_MIN
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expire_in)

    # sub is email, exp is expiry timestamp
    payload = {"sub": subject, "exp": expire_at} 
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

# verifies the signature and expiry
def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return sub
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

# logged-in user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    email = decode_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user