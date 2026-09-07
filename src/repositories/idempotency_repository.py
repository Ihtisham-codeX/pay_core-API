from datetime import datetime, timedelta
from src.database.connection import conn


# Handles lookup and storage of idempotency keys.
#
#  key :  user_id + endpoint + key string
# This means the same UUID can be safely reused on different endpoints
# by different users without any collision.


_KEY_TTL_HOURS = 24   # keys expire after 24 hours

#_________________________________________________________________________________________

def find(key: str, user_id: int, endpoint: str) -> tuple | None:
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, key, user_id, endpoint, response_body, expires_at
        FROM idempotency_keys
        WHERE key = %s AND user_id = %s AND endpoint = %s
          AND expires_at > NOW()
        """,
        (key, user_id, endpoint)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def save(key: str, user_id: int, endpoint: str, response_body: str) -> None:
#_________________________________________________________________________________________

    """Persist an idempotency key together with the response JSON string.
    The response is stored as a raw JSON string so it can be returned
    verbatim on duplicate requests without re-processing anything.
    """
    expires_at = datetime.utcnow() + timedelta(hours=_KEY_TTL_HOURS)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO idempotency_keys (key, user_id, endpoint, response_body, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (key, user_id, endpoint) DO NOTHING
        """,
        (key, user_id, endpoint, response_body, expires_at)
    )
    conn.commit()
    cursor.close()
