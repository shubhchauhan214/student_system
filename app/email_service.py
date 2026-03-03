import smtplib
from email.mime.text import MIMEText
import os

def send_welcome_email(to_email: str, student_name: str):
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    subject = "Welcome to Student System 🎉"
    body = f"""
    Hi {student_name},

    Welcome to our Student Management System!

    We're happy to have you onboard.

    Regards,
    Admin Team
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)