from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from schemas import UserCreate, UserRead, Token
from crud import create_user, get_user_by_email

from mail_service.email_service import send_activation_email
from security import create_activation_token
from security import (
    verify_password,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    hash_password,
)
from database import get_db


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = await create_user(db, user)

    token = create_activation_token(created_user.email)
    send_activation_email(created_user.email, token)

    return created_user


@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account not activated")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserRead:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_user = await get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(db_user)


async def require_admin(current_user: UserRead = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: admins only")
    return current_user


@router.get("/activate")
async def activate_account(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "activation":
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    db_user = await get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_active = True
    await db.commit()
    return {"detail": "Account activated successfully"}
