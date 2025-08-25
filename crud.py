from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film, User
from schemas import FilmCreate, FilmUpdate, UserCreate
from security import hash_password


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
