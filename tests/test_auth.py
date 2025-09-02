import sys
import asyncio
import pytest
import uuid

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from main import app
from models import Base
from schemas import UserCreate
from crud import create_user
from security import create_activation_token
from database import get_db

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
transport = ASGITransport(app=app)
BASE_URL = "http://test"


@pytest.fixture(scope="session")
def event_loop():
    """
    Create and return a new event loop for the test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_session() -> AsyncSession:
    """
    Set up an in-memory async database session with overridden FastAPI dependency.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_factory() as session:

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        yield session

    await engine.dispose()
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_activate_account_success(async_session: AsyncSession):
    """
    Test successful account activation using a valid token.
    """
    email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    password = "12345"
    user_data = UserCreate(email=email, password=password, role="user")
    user = await create_user(async_session, user_data)

    token = create_activation_token(user.email)

    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.get(f"/activate?token={token}")

    assert response.status_code == 200
    assert response.json()["detail"] == "Account activated successfully"


@pytest.mark.anyio
async def test_forgot_password_user_not_found(async_session: AsyncSession):
    """
    Test forgot password flow for a non-existing user.
    """
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post(
            "/forgot_password", params={"email": "unknown@example.com"}
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.anyio
async def test_reset_password_invalid_token(async_session: AsyncSession):
    """
    Test password reset using an invalid token.
    """
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post(
            "/reset_password",
            params={"token": "invalid-token", "new_password": "newpass"},
        )

    assert response.status_code in (400, 422)


@pytest.mark.anyio
async def test_upload_file_success(async_session: AsyncSession):
    """
    Test successful file upload.
    """
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        files = {"file": ("test.txt", b"Hello, world!", "text/plain")}
        response = await client.post("/upload", files=files)

    assert response.status_code == 200
    assert "filename" in response.json()
