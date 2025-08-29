import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from main import app
import uuid


@pytest.mark.asyncio
@patch("mail_service.email_service.send_activation_email")
async def test_register_user(mock_send_email):
    random_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/register", json={
            "email": random_email,
            "password": "testpassword123",
            "role": "user"
        })

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == random_email
        assert data["role"] == "user"
