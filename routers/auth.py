import secrets
import os
import boto3

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer

from models import User
from schemas import UserCreate, UserRead, Token
from crud import (
    create_user,
    get_user_by_email,
    save_reset_token,
    get_user_by_reset_token,
)

from mail_service.email_service import send_activation_email, send_password_reset_email
from security import (
    verify_password,
    create_access_token,
    create_activation_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    hash_password,
    get_current_user,
)
from database import get_db


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


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


@router.post("/forgot_password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = secrets.token_urlsafe(32)
    await save_reset_token(db, user.id, token)
    send_password_reset_email(email, token)
    return {"detail": "Password reset email sent"}


@router.post("/reset_password")
async def reset_password(
    token: str, new_password: str, db: AsyncSession = Depends(get_db)
):
    user_id = await get_user_by_reset_token(db, token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    await db.commit()
    return {"detail": "Password updated successfully"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}


@router.post("/users/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    filename = f"user_{current_user.id}.jpg"
    contents = await file.read()

    s3.put_object(
        Bucket=BUCKET_NAME, Key=filename, Body=contents, ContentType=file.content_type
    )

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if user:
        user.avatar_url = filename
        await db.commit()

    return {"detail": "Avatar uploaded successfully", "avatar_url": filename}


@router.get("/users/me/avatar")
async def get_my_avatar_url(
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user or not user.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar not set")

    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": user.avatar_url},
        ExpiresIn=3600,
    )
    return {"avatar_url": presigned_url}
