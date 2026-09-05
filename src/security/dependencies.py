from fastapi import Request
from src.exceptions.handlers import AdminOnlyException

#_________________________________________________________________________________________

def get_current_user(request: Request) -> dict:
#_________________________________________________________________________________________

    """Return the authenticated user's payload (injected by AuthMiddleware)."""
    return request.state.user

#_________________________________________________________________________________________

def require_admin(request: Request) -> dict:
#_________________________________________________________________________________________

    """Allow access only to users with the 'admin' role."""
    user = request.state.user
    if user.get("role") != "admin":
        raise AdminOnlyException()
    return user
