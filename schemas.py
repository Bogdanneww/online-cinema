from pydantic import BaseModel, EmailStr, ConfigDict


class FilmBase(BaseModel):
    title: str
    genre: str
    price: float


class FilmCreate(FilmBase):
    pass


class FilmUpdate(FilmBase):
    pass


class FilmRead(FilmBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str
