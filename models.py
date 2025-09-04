from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()
"""
Base class for all ORM models.
"""


class User(Base):
    """
    Represents a user in the system.
    Attributes:
        id (int): Primary key.
        email (str): User's email, unique.
        hashed_password (str): Hashed user password.
        role (str): User role (default 'user').
        is_active (bool): Indicates if user is active.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=False)


class Film(Base):
    """
    Represents a film/movie available in the system.
    Attributes:
        id (int): Primary key.
        title (str): Title of the film.
        genre (str): Genre of the film.
        price (float): Price of the film.
    """

    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    genre = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)


class PasswordResetToken(Base):
    """
    Stores password reset tokens for users.
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the user.
        token (str): Unique token string.
        created_at (datetime): Token creation timestamp.
    """

    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
