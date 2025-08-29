from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film, User, PasswordResetToken
from schemas import FilmCreate, FilmUpdate, UserCreate
from utils import hash_password
from datetime import datetime, timedelta


async def create_film(db: AsyncSession, film: FilmCreate):
    new_film = Film(**film.model_dump())
    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)
    return new_film


async def get_film(db: AsyncSession, film_id: int):
    result = await db.execute(select(Film).where(Film.id == film_id))
    film = result.scalar_one_or_none()
    return film


async def get_films(db: AsyncSession):
    result = await db.execute(select(Film))
    films = result.scalars().all()
    return films


async def update_film(db: AsyncSession, film_id: int, film: FilmUpdate):
    result = await db.execute(select(Film).where(Film.id == film_id))
    db_film = result.scalar_one_or_none()
    if not db_film:
        return None

    db_film.title = film.title
    db_film.genre = film.genre
    db_film.price = film.price
    await db.commit()
    await db.refresh(db_film)
    return db_film


async def delete_film(db: AsyncSession, film_id: int):
    result = await db.execute(select(Film).where(Film.id == film_id))
    db_film = result.scalar_one_or_none()
    if not db_film:
        return None
    await db.delete(db_film)
    await db.commit()
    return db_film


async def create_user(db: AsyncSession, user: UserCreate):
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def save_reset_token(db: AsyncSession, user_id: int, token: str):
    reset_token = PasswordResetToken(user_id=user_id, token=token)
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    return reset_token


async def get_user_by_reset_token(db: AsyncSession, token: str):
    expiry_time = datetime.utcnow() - timedelta(hours=24)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.created_at >= expiry_time,
        )
    )
    token_obj = result.scalar_one_or_none()
    return token_obj.user_id if token_obj else None
