from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from security import require_admin
from schemas import FilmCreate, FilmRead, FilmUpdate
from database import get_db
from crud import create_film, get_film, get_films, update_film, delete_film
from models import User


router = APIRouter()


@router.post("/movies/", response_model=FilmRead)
async def add_film(film: FilmCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new film entry.
    """
    new_film = await create_film(db, film)
    return new_film


@router.get("/movies/", response_model=list[FilmRead])
async def list_films(db: AsyncSession = Depends(get_db)):
    """
    Get a list of all films.
    """
    films = await get_films(db)
    return films


@router.get("/movies/{film_id}", response_model=FilmRead)
async def read_film(film_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get details of a film by its ID.
    """
    film = await get_film(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film


@router.put("/movies/{film_id}", response_model=FilmRead)
async def edit_film(film_id: int, film: FilmUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a film's details by ID.
    """
    updated_film = await update_film(db, film_id, film)
    if not updated_film:
        raise HTTPException(status_code=404, detail="Film not found")
    return updated_film


@router.delete("/movies/{film_id}", response_model=FilmRead)
async def remove_film(
    film_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Delete a film (admin only).
    """
    deleted_film = await delete_film(db, film_id)
    if not deleted_film:
        raise HTTPException(status_code=404, detail="Film not found")
    return deleted_film


@router.post("/users/{user_id}/make_admin")
async def make_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Promote a user to admin role (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    user_obj.role = "admin"
    await db.commit()
    return {"detail": "User is now an admin"}
