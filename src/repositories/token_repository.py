from datetime import datetime
from src.database.connection import conn

#_________________________________________________________________________________________

def save(user_id: int, token: str, expires_at: datetime) -> None:
#_________________________________________________________________________________________

    """Persist a new refresh token for the given user."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user_id, token, expires_at)
    )
    conn.commit()
    cursor.close()

#_________________________________________________________________________________________

def find(token: str):
#_________________________________________________________________________________________

    """Return the token row if it exists and has not expired, otherwise None."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, token, expires_at FROM refresh_tokens "
        "WHERE token = %s AND expires_at > NOW()",
        (token,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def revoke(token: str) -> None:
#_________________________________________________________________________________________

    """Delete a single refresh token (logout / rotation)."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (token,))
    conn.commit()
    cursor.close()

#_________________________________________________________________________________________

def revoke_all_for_user(user_id: int) -> None:
#_________________________________________________________________________________________

    """Delete ALL refresh tokens for a user.
    Used when a password changes or an account is suspended and 
    this forces every active session to log in again.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
