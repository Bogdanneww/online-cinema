from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film
from schemas import FilmCreate, FilmRead
from database import get_db

router = APIRouter()

@router.get("/movies/")
async def read_movies():
    return {"message": "List of movies"}

@router.get("/movies/{film_id}", response_model=FilmRead)
async def get_film(film_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Film).where(Film.id == film_id))
    film = result.scalar_one_or_none()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film


@router.post("/movies/", response_model=FilmRead)
async def create_film(film: FilmCreate, db: AsyncSession = Depends(get_db)):
    new_film = Film(**film.model_dump())
    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)
    return new_film
