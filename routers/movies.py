from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film
from schemas import FilmCreate, FilmRead
from database import get_db
from crud import create_film, get_films

router = APIRouter()

@router.post("/movies/", response_model=FilmRead)
async def add_film(film: FilmCreate, db: AsyncSession = Depends(get_db)):
    new_film = await create_film(db, film)
    return new_film

@router.get("/movies/", response_model=list[FilmRead])
async def list_films(db: AsyncSession = Depends(get_db)):
    films = await get_films(db)
    return films


@router.get("/movies/{film_id}", response_model=FilmRead)
async def get_film(film_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Film).where(Film.id == film_id))
    film = result.scalar_one_or_none()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
