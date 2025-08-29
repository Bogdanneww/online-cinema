import os
from dotenv import load_dotenv

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import get_user_by_email
from schemas import UserRead


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_activation_token(email: str):
    return create_access_token({"sub": email, "type": "activation"})


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token missing subject")

    db_user = await get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account is not activated")

    return UserRead.from_orm(db_user)


async def require_admin(current_user: UserRead = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: admins only")
    return current_user
