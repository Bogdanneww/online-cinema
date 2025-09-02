from unittest import mock
import pytest
from mail_service.email_service import (
    send_email,
    send_activation_email,
    send_password_reset_email,
)


@pytest.fixture
def mock_send_email():
    """
    Pytest fixture that patches smtplib.SMTP to mock email sending.
    Yields the mocked SMTP class.
    """
    with mock.patch("smtplib.SMTP") as mock_smtp:
        yield mock_smtp


def test_send_email(mock_send_email):
    """
    Test that send_email function initializes SMTP connection
    with the correct server and port.
    """
    mock_server = mock_send_email.return_value
    send_email("test@example.com", "Test Subject", "This is a test email body.")
    mock_send_email.assert_called_once_with("smtp.test.com", 587)


def test_send_activation_email(mock_send_email):
    """
    Test that send_activation_email function calls SMTP with correct parameters.
    """
    mock_server = mock_send_email.return_value
    send_activation_email("test@example.com", "test_token")
    mock_send_email.assert_called_once_with("smtp.test.com", 587)


def test_send_password_reset_email(mock_send_email):
    """
    Test that send_password_reset_email function calls SMTP with correct parameters.
    """
    mock_server = mock_send_email.return_value
    send_password_reset_email("test@example.com", "test_reset_token")
    mock_send_email.assert_called_once_with("smtp.test.com", 587)
