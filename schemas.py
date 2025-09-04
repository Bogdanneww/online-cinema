from pydantic import BaseModel, EmailStr, ConfigDict


class FilmBase(BaseModel):
    """Base schema for a film."""

    title: str
    genre: str
    price: float


class FilmCreate(FilmBase):
    """Schema for creating a new film."""

    pass


class FilmUpdate(FilmBase):
    """Schema for updating an existing film."""

    pass


class FilmRead(FilmBase):
    """Schema for reading film data (includes ID)."""

    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base schema for a user (email only)."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str
    role: str = "user"


class UserRead(UserBase):
    """Schema for reading user data (includes ID and role)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str


class Token(BaseModel):
    """Schema for returning authentication tokens."""

    access_token: str
    token_type: str
