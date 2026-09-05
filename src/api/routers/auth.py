from fastapi import APIRouter, Response, Cookie
from src.schemas.auth    import RegisterRequest, LoginRequest
from src.services        import auth_service
from src.security.cookies import set_auth_cookies, delete_auth_cookies
from src.exceptions.handlers import MissingRefreshTokenException




router = APIRouter(prefix="/auth", tags=["Authentication"])


#_________________________________________________________________________________________

@router.post("/register", status_code=201)
#_________________________________________________________________________________________

def register(body: RegisterRequest):
    """
    Register a new user.

    Workflow:
      RegisterRequest (validated by Pydantic) → auth_service.register()
      → creates user + wallet → returns confirmation
    """
    return auth_service.register(
        email      = body.email,
        username   = body.username,
        password   = body.password,
        first_name = body.first_name,
        last_name  = body.last_name,
        phone      = body.phone,
    )


#_________________________________________________________________________________________

@router.post("/login")
#_________________________________________________________________________________________

def login(body: LoginRequest, response: Response):
    """
    Authenticate a user and issue tokens as HttpOnly cookies.

    Workflow:
      Credentials → auth_service.login() → access + refresh tokens
      → written to cookies → client never sees the raw tokens
    """
    access_token, refresh_token = auth_service.login(body.email, body.password)
    set_auth_cookies(response, access_token, refresh_token)
    return {"message": "Login successful."}


#_________________________________________________________________________________________

@router.post("/refresh")
#_________________________________________________________________________________________

def refresh(response: Response, refresh_token: str = Cookie(None)):
    """
    Rotate tokens: exchange a valid refresh token for a new pair.

    Workflow:
      Old refresh token (cookie) → auth_service.refresh()
      → old token revoked → new pair issued → new cookies set
    """
    if refresh_token is None:
        raise MissingRefreshTokenException()

    new_access, new_refresh = auth_service.refresh(refresh_token)
    set_auth_cookies(response, new_access, new_refresh)
    return {"message": "Tokens refreshed successfully."}

#_________________________________________________________________________________________

@router.post("/logout")
#_________________________________________________________________________________________

def logout(response: Response, refresh_token: str = Cookie(None)):
    """
    Revoke the refresh token and clear auth cookies.

    Workflow:
      refresh_token (cookie) → auth_service.logout() → DB token deleted
      → cookies cleared → session ended
    """
    auth_service.logout(refresh_token)
    delete_auth_cookies(response)
    return {"message": "Logged out successfully."}
