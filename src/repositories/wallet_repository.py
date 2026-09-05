from src.database.connection import conn
from src.config import settings

#_________________________________________________________________________________________

def create_wallet(user_id: int) -> tuple:
#_________________________________________________________________________________________

    """Create a wallet for a user with zero balance."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO wallets (user_id, currency)
        VALUES (%s, %s)
        RETURNING id, user_id, balance, currency, status, created_at, updated_at
        """,
        (user_id, settings.DEFAULT_CURRENCY)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_by_user_id(user_id: int) -> tuple | None:
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, balance, currency, status, created_at, updated_at "
        "FROM wallets WHERE user_id = %s",
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_by_wallet_id(wallet_id: int) -> tuple | None:
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, balance, currency, status, created_at, updated_at "
        "FROM wallets WHERE id = %s",
        (wallet_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_for_update(wallet_id: int, cursor) -> tuple | None:
#_________________________________________________________________________________________

    """Fetch a wallet row and LOCK it for the duration of this DB transaction.
    SELECT ... FOR UPDATE acquires a row-level lock in PostgreSQL.
    Any other transaction trying to lock or modify this row will WAIT
    until this transaction commits or rolls back.

    This is what prevents the double-spend race condition:
      Two transfers from the same wallet execute simultaneously 
      the second one waits at this line until the first finishes 
      then reads the already-updated balance and decides correctly.
    """
    cursor.execute(
        "SELECT id, user_id, balance, currency, status, created_at, updated_at "
        "FROM wallets WHERE id = %s FOR UPDATE",
        (wallet_id,)
    )
    return cursor.fetchone()

#_________________________________________________________________________________________

def debit(wallet_id: int, amount: int, cursor) -> None:
#_________________________________________________________________________________________

    cursor.execute(
        "UPDATE wallets SET balance = balance - %s WHERE id = %s",
        (amount, wallet_id)
    )

#_________________________________________________________________________________________

def credit(wallet_id: int, amount: int, cursor) -> None:
#_________________________________________________________________________________________

    cursor.execute(
        "UPDATE wallets SET balance = balance + %s WHERE id = %s",
        (amount, wallet_id)
    )
