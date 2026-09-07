from datetime import datetime, timedelta

from src.config import settings
from src.security.hashing import hash_password, verify_password
from src.security.jwt    import create_access_token, create_refresh_token, verify_refresh_token
from src.repositories    import user_repository, token_repository, wallet_repository
from src.services        import audit_service
from src.exceptions.handlers import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountSuspendedException,
    InvalidRefreshTokenException,
    RefreshTokenRevokedException,
)

#_________________________________________________________________________________________

def register(email: str, username: str, password: str, first_name: str, last_name: str, phone: str | None) -> dict:
#_________________________________________________________________________________________

    if user_repository.find_by_email(email):
        raise UserAlreadyExistsException()

    if user_repository.find_by_username(username):
        raise UserAlreadyExistsException()

    hashed = hash_password(password)

    user_row = user_repository.create_user(
        email, username, hashed, first_name, last_name, phone, role="user"
    )

    # Every user gets a wallet at registration.
    wallet_repository.create_wallet(user_id=user_row[0])

    audit_service.log(
        user_id     = user_row[0],
        action      = audit_service.USER_REGISTERED,
        resource    = "user",
        resource_id = str(user_row[0]),
    )

    return {
        "message":    "Account created successfully.",
        "user_id":    user_row[0],
        "email":      user_row[1],
        "username":   user_row[2],
        "first_name": user_row[4],
        "last_name":  user_row[5],
    }
#_________________________________________________________________________________________

def login(email: str, password: str) -> tuple[str, str]:
#_________________________________________________________________________________________

    user_row = user_repository.find_by_email(email)

    if user_row is None:
        raise InvalidCredentialsException()

    # user_row[3] = password_hash column
    if not verify_password(password, user_row[3]):
        raise InvalidCredentialsException()

    # user_row[8] = status column
    if user_row[8] != "active":
        raise AccountSuspendedException()

    token_payload = {
        "user_id":  user_row[0],
        "email":    user_row[1],
        "username": user_row[2],
        "role":     user_row[7],   # user_row[7] = role column
    }

    access_token  = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    token_repository.save(user_row[0], refresh_token, expires_at)

    audit_service.log(
        user_id     = user_row[0],
        action      = audit_service.USER_LOGIN,
        resource    = "user",
        resource_id = str(user_row[0]),
    )

    return access_token, refresh_token
#_________________________________________________________________________________________

def refresh(refresh_token: str) -> tuple[str, str]:
#_________________________________________________________________________________________

    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise InvalidRefreshTokenException()

    db_token = token_repository.find(refresh_token)
    if db_token is None:
        raise RefreshTokenRevokedException()

    # Delete the old token — one-time use (rotation)
    token_repository.revoke(refresh_token)

    token_payload = {
        "user_id":  payload.get("user_id"),
        "email":    payload.get("email"),
        "username": payload.get("username"),
        "role":     payload.get("role"),
    }

    new_access_token  = create_access_token(token_payload)
    new_refresh_token = create_refresh_token(token_payload)

    expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    token_repository.save(token_payload["user_id"], new_refresh_token, expires_at)

    return new_access_token, new_refresh_token
#_________________________________________________________________________________________

def logout(refresh_token: str | None, user_id: int | None = None) -> None:

    if refresh_token:
        token_repository.revoke(refresh_token)

    if user_id:
        audit_service.log(
            user_id     = user_id,
            action      = audit_service.USER_LOGOUT,
            resource    = "user",
            resource_id = str(user_id),
        )
