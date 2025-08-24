from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film
from schemas import FilmCreate

async def create_film(db: AsyncSession, film: FilmCreate):
    new_film = Film(**film.model_dump())
    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)
    return new_film

async def get_films(db: AsyncSession):
    result = await db.execute(select(Film))
    films = result.scalars().all()
    return films
