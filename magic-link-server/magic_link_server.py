# uvicorn magic_link_server:app --reload --port 8000 
# curl http://localhost:8000/send-magic-link -X POST -H "Content-Type: application/json" -d '{"email": "test@example.com"}'

# curl http://localhost:8000/token-store

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import uuid
import redis
import os
import smtplib
from email.message import EmailMessage

app = FastAPI()

# Redis connection (from Docker environment)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

MAGIC_LINK_BASE_URL = os.getenv("MAGIC_LINK_BASE_URL", "http://localhost:3000")

class EmailRequest(BaseModel):
    email: str

@app.post("/send-magic-link")
def send_magic_link(data: EmailRequest):
    token = str(uuid.uuid4())
    r.setex(token, 900, data.email)  # 15 minutes expiration
    link = f"{MAGIC_LINK_BASE_URL}/api/v1/auths/magic-login?token={token}"

    msg = EmailMessage()
    msg.set_content(f"Click here to log in: {link}")
    msg["Subject"] = "Your Magic Link"
    msg["From"] = "no-reply@example.com"
    msg["To"] = data.email

    try:
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "magic link sent", "link": link}

# Debug route (optional)
@app.get("/token-store")
def debug_tokens():
    tokens = r.keys("*")
    data = {token: r.get(token) for token in tokens}
    # {  "token1": "email1@example.com",
    #    "token2": "email2@example.com", ...}
    return data
