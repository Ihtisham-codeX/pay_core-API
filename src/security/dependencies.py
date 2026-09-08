from fastapi import Request
from src.exceptions.handlers import (
    AdminOnlyException,
    RateLimitExceededException,
    RedisUnavailableException,
)
from src.services.redis_service import RedisService, RedisUnavailableError

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


def enforce_user_rate_limit(request: Request) -> None:
    """Fixed-window limiter keyed by authenticated user. Fail closed if Redis is down."""
    user = request.state.user
    redis_svc = RedisService()
    key = redis_svc.rate_limit_key(user["user_id"])
    try:
        allowed = redis_svc.check_rate_limit(key)
    except RedisUnavailableError:
        raise RedisUnavailableException()
    if not allowed:
        raise RateLimitExceededException()
