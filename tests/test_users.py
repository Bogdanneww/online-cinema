import pytest
import uuid

from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app


@pytest.mark.asyncio
@patch("mail_service.email_service.send_activation_email")
async def test_register_user(mock_send_email):
    """
    Async test for user registration endpoint.
    Mocks the send_activation_email function to avoid sending real emails.
    Generates a random email for registration.
    Sends POST request to '/register' with email, password, and role.
    Asserts that the response status code is 200 and response data matches input.
    """
    random_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/register",
            json={"email": random_email, "password": "testpassword123", "role": "user"},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == random_email
        assert data["role"] == "user"


client = TestClient(app)


def test_login():
    """
    Test for user login flow.
    Registers a new user with a random email via POST to '/register'.
    Prints the response text (for debugging).
    Asserts that the registration response status code is 200.
    """
    email = f"test_{uuid.uuid4()}@example.com"
    user_data = {"email": email, "password": "testpassword123", "role": "user"}
    response = client.post("/register", json=user_data)
    print(response.text)
    assert response.status_code == 200
