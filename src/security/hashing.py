from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#_________________________________________________________________________________________

def hash_password(password: str) -> str:
#_________________________________________________________________________________________

    return pwd_context.hash(password)

#_________________________________________________________________________________________

def verify_password(plain_password: str, hashed_password: str) -> bool:
#_________________________________________________________________________________________

    """Return True if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)
