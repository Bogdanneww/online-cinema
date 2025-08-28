from email.mime.text import MIMEText
import os, smtplib
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@yourapp.com")


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("Email sent")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_activation_email(user_email: str, token: str):
    link = f"http://localhost:8000/activate?token={token}"
    subject = "Activate your account"
    body = f"Hello!\nClick this link to activate your account:\n{link}"
    send_email(user_email, subject, body)


def send_password_reset_email(user_email: str, token: str):
    reset_link = f"http://localhost:8000/reset_password?token={token}"
    subject = "Reset your password"
    body = f"Click the link to reset your password:\n{reset_link}\n\nThis link will expire in 24 hours."
    send_email(user_email, subject, body)
