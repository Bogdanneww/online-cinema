from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    param password: The plain password to hash.
    return: Hashed password as a string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    param plain_password: The input password to check.
    param hashed_password: The stored hashed password.
    return: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
