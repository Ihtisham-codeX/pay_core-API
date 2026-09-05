from fastapi import Response
from src.config import settings


# Why HttpOnly cookies?
#   - JavaScript cannot read HttpOnly cookies so it protects against XSS attacks.
#   - Automatically sent with every request so no manual header handling.
#   - SameSite=lax prevents CSRF on most modern browsers.
#
# Why no `domain` parameter locally?
#   Setting domain="localhost" explicitly causes strict domain-matching rules
#   in Postman and browsers that reject the cookie. Omitting `domain` lets the
#   server automatically scope the cookie to whatever host the request came from.
#_________________________________________________________________________________________

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
#_________________________________________________________________________________________

    """Write both tokens as secure HttpOnly cookies."""

    response.set_cookie(
        key      = "access_token",
        value    = access_token,
        httponly = True,
        samesite = "lax",
        max_age  = settings.JWT_EXPIRE_MINUTES * 60,         # seconds
    )

    response.set_cookie(
        key      = "refresh_token",
        value    = refresh_token,
        httponly = True,
        samesite = "lax",
        max_age  = settings.JWT_REFRESH_EXPIRE_DAYS * 86400, # seconds
    )

#_________________________________________________________________________________________

def delete_auth_cookies(response: Response) -> None:
#_________________________________________________________________________________________

    """Clear both auth cookies on logout."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
