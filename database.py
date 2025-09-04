from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
"""
Async SQLAlchemy engine instance connected to the SQLite database at './online_cinema.db'.
"""
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)
"""
Async sessionmaker factory that generates AsyncSession instances
for interacting with the database.
expire_on_commit=False prevents automatic expiration of objects after commit.
"""


async def get_db():
    """
    Async generator function to provide a database session for dependency injection.
    Yields:
        AsyncSession: An asynchronous SQLAlchemy session instance.
    Usage:
        This function is intended to be used as a FastAPI dependency
        to provide a database session for route handlers.
    """
    async with SessionLocal() as session:
        yield session
