from pydantic_settings import BaseSettings
from pydantic import EmailStr
from dotenv import load_dotenv


# Load environment variables from a .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a `.env` file.
    Attributes:
        SECRET_KEY (str): Secret key used for signing tokens and application security.
        AWS_ACCESS_KEY_ID (str): AWS access key ID.
        AWS_SECRET_ACCESS_KEY (str): AWS secret access key.
        AWS_REGION (str): AWS region, e.g., 'us-east-1'.
        AWS_BUCKET_NAME (str): Name of the AWS S3 bucket.
        EMAIL_HOST (str): SMTP server host for sending emails.
        EMAIL_PORT (int): SMTP server port, default is 587.
        EMAIL_USER (str): Username for SMTP authentication.
        EMAIL_PASS (str): Password for SMTP authentication.
        EMAIL_FROM (EmailStr): Default sender email address.
    """

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

    DATABASE_URL: str = "sqlite+aiosqlite:///./online_cinema.db"
    SYNC_DATABASE_URL: str = "sqlite:///./online_cinema.db"

    class Config:
        """
        Configuration for Pydantic settings.
        Specifies that environment variables can be loaded from a `.env` file.
        """

        env_file = ".env"


settings = Settings()
