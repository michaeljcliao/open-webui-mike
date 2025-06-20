from open_webui.models.users import Users
from open_webui.models.auths import (
    AddUserForm,
    ApiKey,
    Auths,
    Token,
    LdapForm,
    SigninForm,
    SigninResponse,
    SignupForm,
    UpdatePasswordForm,
    UpdateProfileForm,
    UserResponse,
)
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
import redis
import uuid
import time
import datetime

from open_webui.utils.auth import create_token
from open_webui.utils.misc import parse_duration
from open_webui.utils.access_control import get_permissions
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import (
    WEBUI_AUTH,
    WEBUI_AUTH_TRUSTED_EMAIL_HEADER,
    WEBUI_AUTH_TRUSTED_NAME_HEADER,
    WEBUI_AUTH_COOKIE_SAME_SITE,
    WEBUI_AUTH_COOKIE_SECURE,
    SRC_LOG_LEVELS,
)

from open_webui.routers.auths import signup

router = APIRouter()

# Redis connection (shared with magic-link-server)
r = redis.Redis(host="redis", port=6379, decode_responses=True)

@router.get("/auth/magic-login")
async def magic_login(request: Request, response: Response, token: str):
    email = r.get(token)
    if not email:
        raise HTTPException(400, detail="Invalid or expired token")

    r.delete(token)

    # Auto-signup user if not exists
    if not Users.get_user_by_email(email.lower()):
        await signup(
            request,
            response,
            SignupForm(
                email=email,
                password=str(uuid.uuid4()),  # dummy password
                name=email.split("@")[0]
            )
        )

    # Authenticate user
    user = Auths.authenticate_user_by_trusted_header(email.lower())
    if not user:
        raise HTTPException(401, detail="Authentication failed")

    # Generate JWT token
    expires_delta = parse_duration(request.app.state.config.JWT_EXPIRES_IN)
    expires_at = None
    if expires_delta:
        expires_at = int(time.time()) + int(expires_delta.total_seconds())

    token = create_token(data={"id": user.id}, expires_delta=expires_delta)

    datetime_expires_at = (
        datetime.datetime.fromtimestamp(expires_at, datetime.timezone.utc)
        if expires_at
        else None
    )

    # Set the JWT cookie
    response.set_cookie(
        key="token",
        value=token,
        expires=datetime_expires_at,
        httponly=True,
        samesite=WEBUI_AUTH_COOKIE_SAME_SITE,
        secure=WEBUI_AUTH_COOKIE_SECURE,
    )

    # Optional: return structured info (useful if accessed via XHR)
    user_permissions = get_permissions(
        user.id, request.app.state.config.USER_PERMISSIONS
    )

    # Redirect back to home (you can change this if used in XHR or iframe)
    return RedirectResponse(url="/")

