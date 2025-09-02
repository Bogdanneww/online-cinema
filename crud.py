from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Film, User, PasswordResetToken
from schemas import FilmCreate, FilmUpdate, UserCreate
from utils import hash_password
from datetime import datetime, timedelta


async def create_film(db: AsyncSession, film: FilmCreate):
    """
    Create a new film record in the database.
    Args:
        db (AsyncSession): The database session.
        film (FilmCreate): The film data to create.
    Returns:
        Film: The created Film object.
    """
    new_film = Film(**film.model_dump())
    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)
    return new_film


async def get_film(db: AsyncSession, film_id: int):
    """
    Retrieve a film by its ID.
    Args:
        db (AsyncSession): The database session.
        film_id (int): The ID of the film to retrieve.
    Returns:
        Film | None: The Film object if found, else None.
    """
    result = await db.execute(select(Film).where(Film.id == film_id))
    film = result.scalar_one_or_none()
    return film


async def get_films(db: AsyncSession):
    """
    Retrieve all films from the database.
    Args:
        db (AsyncSession): The database session.
    Returns:
        list[Film]: List of all Film objects.
    """
    result = await db.execute(select(Film))
    films = result.scalars().all()
    return films


async def update_film(db: AsyncSession, film_id: int, film: FilmUpdate):
    """
    Update an existing film record by its ID.
    Args:
        db (AsyncSession): The database session.
        film_id (int): The ID of the film to update.
        film (FilmUpdate): The film data to update.
    Returns:
        Film | None: The updated Film object if found, else None.
    """
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
    """
    Delete a film record by its ID.
    Args:
        db (AsyncSession): The database session.
        film_id (int): The ID of the film to delete.
    Returns:
        Film | None: The deleted Film object if found, else None.
    """
    result = await db.execute(select(Film).where(Film.id == film_id))
    db_film = result.scalar_one_or_none()
    if not db_film:
        return None
    await db.delete(db_film)
    await db.commit()
    return db_film


async def create_user(db: AsyncSession, user: UserCreate):
    """
     Create a new user with hashed password.
    Args:
         db (AsyncSession): The database session.
         user (UserCreate): The user data to create.
    Returns:
        User: The created User object.
    """
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieve a user by email.
    Args:
        db (AsyncSession): The database session.
        email (str): The email address to search for.
    Returns:
        User | None: The User object if found, else None.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def save_reset_token(db: AsyncSession, user_id: int, token: str):
    """
    Save a password reset token for a user.
    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.
        token (str): The reset token string.
    Returns:
        PasswordResetToken: The created PasswordResetToken object.
    """
    reset_token = PasswordResetToken(user_id=user_id, token=token)
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    return reset_token


async def get_user_by_reset_token(db: AsyncSession, token: str):
    """
    Retrieve a user ID by a valid password reset token.
    Tokens older than 24 hours are considered expired.
    Args:
        db (AsyncSession): The database session.
        token (str): The reset token string.
    Returns:
        int | None: The user ID if token is valid, else None.
    """
    expiry_time = datetime.utcnow() - timedelta(hours=24)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.created_at >= expiry_time,
        )
    )
    token_obj = result.scalar_one_or_none()
    return token_obj.user_id if token_obj else None
