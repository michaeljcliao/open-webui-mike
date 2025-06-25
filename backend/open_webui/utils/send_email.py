import smtplib
from email.message import EmailMessage
import os


from open_webui.env import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD

print("Email configuration loaded from environment variables."
      f" Host: {EMAIL_HOST}, Port: {EMAIL_PORT}, Username: {EMAIL_USERNAME}")

def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USERNAME
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.send_message(msg)
