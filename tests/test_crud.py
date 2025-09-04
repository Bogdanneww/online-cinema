import pytest
import pytest_asyncio
import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    func,
    Boolean,
)
from datetime import datetime, timedelta
from pydantic import BaseModel

from crud import (
    create_film,
    get_film,
    get_films,
    update_film,
    delete_film,
    create_user,
    get_user_by_email,
    save_reset_token,
    get_user_by_reset_token,
)

Base = declarative_base()


class Film(Base):
    """
    SQLAlchemy model for the 'films' table.
    Attributes: id, title, genre, price.
    """

    __tablename__ = "films"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    genre = Column(String)
    price = Column(Float)


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    Attributes: id, email, hashed_password, role, is_active.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=False, nullable=False)


class PasswordResetToken(Base):
    """
    SQLAlchemy model for the 'password_resets' table.
    Stores password reset tokens with timestamps.
    """

    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())


class FilmCreate(BaseModel):
    """
    Pydantic schema for creating a Film.
    Fields: title, genre, price.
    """

    title: str
    genre: str
    price: float


class FilmUpdate(BaseModel):
    """
    Pydantic schema for updating a Film.
    Fields: title, genre, price.
    """

    title: str
    genre: str
    price: float


class UserCreate(BaseModel):
    """
    Pydantic schema for creating a User.
    Fields: email, password, role.
    """

    email: str
    password: str
    role: str


def hash_password(password: str) -> str:
    """
    Dummy hash function for password.
    Replace with real hashing in production.
    """
    return "hashed_" + password


@pytest_asyncio.fixture(scope="function")
async def async_session():
    """
    Creates a new in-memory SQLite async session for each test.
    Sets up and tears down database tables around tests.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_and_get_film(async_session: AsyncSession):
    """
    Test creating a film and retrieving it by ID.
    """
    film_data = FilmCreate(title="Test Film", genre="Action", price=9.99)
    new_film = await create_film(async_session, film_data)
    assert new_film.id is not None
    assert new_film.title == "Test Film"

    fetched = await get_film(async_session, new_film.id)
    assert fetched.title == "Test Film"


@pytest.mark.asyncio
async def test_get_films(async_session: AsyncSession):
    """
    Test retrieving a list of films after creating multiple entries.
    """
    film_data1 = FilmCreate(title="Film1", genre="Genre1", price=1.0)
    film_data2 = FilmCreate(title="Film2", genre="Genre2", price=2.0)
    await create_film(async_session, film_data1)
    await create_film(async_session, film_data2)

    films = await get_films(async_session)
    assert isinstance(films, list)
    assert len(films) >= 2


@pytest.mark.asyncio
async def test_update_film(async_session: AsyncSession):
    """
    Test updating film details and verifying changes.
    """
    film_data = FilmCreate(title="Old Title", genre="Drama", price=5.00)
    film = await create_film(async_session, film_data)

    update_data = FilmUpdate(title="New Title", genre="Comedy", price=7.50)
    updated = await update_film(async_session, film.id, update_data)

    assert updated.title == "New Title"
    assert updated.genre == "Comedy"
    assert updated.price == 7.50


@pytest.mark.asyncio
async def test_delete_film(async_session: AsyncSession):
    """
    Test deleting a film and confirming it no longer exists.
    """
    film_data = FilmCreate(title="To Delete", genre="Horror", price=4.00)
    film = await create_film(async_session, film_data)

    deleted = await delete_film(async_session, film.id)
    assert deleted.id == film.id

    should_be_none = await get_film(async_session, film.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_create_and_get_user(async_session: AsyncSession):
    """
    Test user creation and retrieval by email.
    Also checks password hashing correctness using bcrypt.
    """
    user_data = UserCreate(email="test@example.com", password="12345", role="user")
    user = await create_user(async_session, user_data)

    fetched = await get_user_by_email(async_session, "test@example.com")
    assert fetched.email == "test@example.com"
    assert bcrypt.checkpw(user_data.password.encode(), fetched.hashed_password.encode())


@pytest.mark.asyncio
async def test_save_and_get_reset_token(async_session: AsyncSession):
    """
    Test saving a password reset token and retrieving the associated user ID.
    """
    user_data = UserCreate(email="reset@example.com", password="resetpass", role="user")
    user = await create_user(async_session, user_data)

    token = "reset-token-123"
    saved_token = await save_reset_token(async_session, user.id, token)

    fetched_user_id = await get_user_by_reset_token(async_session, token)
    assert fetched_user_id == user.id


@pytest.mark.asyncio
async def test_expired_reset_token(async_session: AsyncSession):
    """
    Test that an expired password reset token is not accepted.
    """
    user_data = UserCreate(email="expired@example.com", password="expired", role="user")
    user = await create_user(async_session, user_data)

    old_token = PasswordResetToken(
        user_id=user.id,
        token="old-token",
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    async_session.add(old_token)
    await async_session.commit()

    result = await get_user_by_reset_token(async_session, "old-token")
    assert result is None
