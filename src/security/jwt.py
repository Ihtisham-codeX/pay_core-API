from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.config import settings



#_________________________________________________________________________________________

def create_access_token(data: dict) -> str:
#_________________________________________________________________________________________

    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

#_________________________________________________________________________________________

def verify_access_token(token: str) -> dict | None: 
#_________________________________________________________________________________________

    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]) # checks if the decoded signature matches 
    except JWTError:
        return None


#_________________________________________________________________________________________

def create_refresh_token(data: dict) -> str:
#_________________________________________________________________________________________

    payload = data.copy()
    payload["exp"]  = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload["type"] = "refresh"   # type claim distinguishes refresh from access tokens
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

#_________________________________________________________________________________________

def verify_refresh_token(token: str) -> dict | None:
#_________________________________________________________________________________________

    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # Reject a token that is not explicitly typed as "refresh"
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
