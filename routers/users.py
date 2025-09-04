from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud import get_user_by_email
from database import get_db
from routers.auth import get_current_user
from schemas import UserRead
from utils import hash_password

router = APIRouter()


@router.get("/users/")
async def read_users():
    """
    Return a placeholder message for a list of users.
    """
    return {"message": "List of users"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: UserRead = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return current_user


@router.post("/reset_password")
async def reset_password(
    email: str, new_password: str, db: AsyncSession = Depends(get_db)
):
    """
    Reset the password for the user with the given email.
    """
    db_user = await get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.hashed_password = hash_password(new_password)
    await db.commit()
    return {"detail": "Password updated"}
