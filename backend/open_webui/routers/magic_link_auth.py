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
from fastapi.responses import RedirectResponse, HTMLResponse
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

from open_webui.config import WEBUI_URL, OPENID_PROVIDER_URL, ENABLE_OAUTH_SIGNUP

from open_webui.routers.auths import signup, signout, signin

router = APIRouter()

# Redis connection (shared with magic-link-server)
# r = redis.Redis(host="redis", port=6379, decode_responses=True) # For Docker
r = redis.Redis(host="localhost", port=6379, decode_responses=True) # for dev.sh

@router.get("") # allows /auth/magic-login instead of /auth/magic-login/
async def magic_login(request: Request, response: Response, magic_token: str):
    # Skip the redis setup and user self sign up
    # email = r.get(magic_token)
    # print(f"email from redis: {email}")
    # if not email:
    #     raise HTTPException(400, detail="Invalid or expired token")

    # # Check if the user exists, if not, create a new user with a random password
    # if not Users.get_user_by_email(email.lower()):
    #     print(f"User {email} not found, creating new user")
    #     await signup(
    #         request,
    #         response,
    #         SignupForm(
    #         email=email,
    #         password=str(uuid.uuid4()),
    #         name=email.split("@")[0]
    #         )
    #     )
    # user = Users.get_user_by_email(email.lower())
    # user = Auths.authenticate_user_by_trusted_header(email.lower())
    print(f"Magic token: {magic_token}")
    magic_link = f"{WEBUI_URL}/magic?magic_token={magic_token}"
    print(f"Magic link: {magic_link}")
    user = Users.get_user_by_magic_link(magic_link)
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

    # Make /auth/magic-login Serve an HTML Page (or a Clean Blank) 
    # That Your Frontend JS Can Handle
    # Replace the FastAPI endpoint to return a minimal HTML page or redirect
    #  via JS that can hand off to your frontend. 
    html_content = """
    <!DOCTYPE html>
    <html>
      <head><title>Magic Login</title></head>
      <body>
        <script>
          window.location.href = window.location.origin + '/?magic_token=' + encodeURIComponent('""" + magic_token + """');
        </script>
        <p>Logging you in...</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

    redirect_url = WEBUI_URL
    print(f"Redirecting to: {redirect_url}")
    redir_res = RedirectResponse(url=redirect_url, status_code=302)
    redir_res.delete_cookie("token")
    redir_res.set_cookie(
        key="token",
        value=user_token,
        expires=datetime_expires_at,
        httponly=True,
        samesite=WEBUI_AUTH_COOKIE_SAME_SITE,
        secure=WEBUI_AUTH_COOKIE_SECURE,
    )
    return redir_res
    # expires_http = datetime.datetime.fromtimestamp(
    #     expires_at, 
    #     tz=datetime.timezone.utc).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
    # redirect_response.headers["Set-Cookie"] = (
    #     f"token={token}; "
    #     f"Path=/; "
    #     f"HttpOnly; "
    #     f"SameSite={WEBUI_AUTH_COOKIE_SAME_SITE}; "
    #     f"{'Secure; ' if WEBUI_AUTH_COOKIE_SECURE else ''}"
    #     f"Expires={expires_http}"
    # )

    # r.delete(token) # Don't delete the token


    # Sign out
    # response = await signout(request, response)

    # password unused if trusted header is set
    # form_data = SigninForm(email=email, password="dummy")  

    # # Simulate trusted header
    # request.headers.__dict__["_list"].append((
    #     b"x-user-email", email.encode()
    # ))

    # # Now invoke the real signin route
    # signin_response = await signin(request, response, form_data)

    # redirect_response = RedirectResponse(
    #     headers=signin_response.headers,
    #     url="/",
    #     status_code=302
    # )
    # # redirect_response.set_cookie(
    # #     key="token",
    # #     value=signin_response["token"],
    # #     httponly=True,
    # #     samesite="Lax",  # Adjust as needed
    # #     secure=True,  # Adjust based on your environment
    # # )

    # return redirect_response
