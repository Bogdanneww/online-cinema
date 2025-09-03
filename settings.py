from pydantic_settings import BaseSettings
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str

    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASS: str
    EMAIL_FROM: EmailStr = "noreply@yourapp.com"

    class Config:
        env_file = ".env"


settings = Settings()
