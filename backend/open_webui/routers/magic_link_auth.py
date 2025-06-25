from open_webui.models.users import Users

from fastapi import APIRouter, Request, Response, HTTPException
import uuid
import time
import datetime

from open_webui.utils.auth import create_token
from open_webui.utils.misc import parse_duration
from open_webui.utils.access_control import get_permissions
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import (
    WEBUI_AUTH_COOKIE_SAME_SITE,
    WEBUI_AUTH_COOKIE_SECURE,
)

router = APIRouter()

@router.get("") # allows /auth/magic-login instead of /auth/magic-login/
async def magic_login(request: Request, response: Response, magic_token: str):
    # Validate the magic token
    user = Users.get_user_by_magic_token(magic_token)
    print(f"Magic login user_id: {user.id}")

    expires_delta = parse_duration(request.app.state.config.JWT_EXPIRES_IN)
    expires_at = None
    if expires_delta:
        expires_at = int(time.time()) + int(expires_delta.total_seconds())

    user_token = create_token(
        data={"id": user.id},
        expires_delta=expires_delta,
        )
    print(f"Generated token: {user_token}")

    datetime_expires_at = (
        datetime.datetime.fromtimestamp(expires_at, datetime.timezone.utc)
        if expires_at else None
    )

    # Create redirect response and delete the previous token
    # Sign out first to ensure the token is cleared
    # Set cookie manually for the client
    response.delete_cookie("token")
    response.set_cookie(
        key="token",
        value=user_token,
        expires=datetime_expires_at,
        httponly=True,
        samesite=WEBUI_AUTH_COOKIE_SAME_SITE,
        secure=WEBUI_AUTH_COOKIE_SECURE,
    )

    user_permissions = get_permissions(
        user.id, request.app.state.config.USER_PERMISSIONS
    )

    
    return {
        "token": user_token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "profile_image_url": user.profile_image_url,
        "permissions": user_permissions,
    }