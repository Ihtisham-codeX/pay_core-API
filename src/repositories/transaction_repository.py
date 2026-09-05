from src.database.connection import conn

#_________________________________________________________________________________________

def insert_transaction(reference: str, sender_wallet_id: int, receiver_wallet_id: int, 
                       amount: int, currency: str, cursor) -> tuple:
#_________________________________________________________________________________________
    
    """Insert a completed transaction record. Returns the full row."""
    cursor.execute(
        """
        INSERT INTO transactions
            (reference, sender_wallet_id, receiver_wallet_id, amount, currency, type, status)
        VALUES (%s, %s, %s, %s, %s, 'transfer', 'completed')
        RETURNING id, reference, sender_wallet_id, receiver_wallet_id,
                  amount, currency, type, status, created_at
        """,
        (reference, sender_wallet_id, receiver_wallet_id, amount, currency)
    )
    return cursor.fetchone()

#_________________________________________________________________________________________

def insert_ledger_entry(transaction_id: int, wallet_id: int,
                        entry_type: str, amount: int, cursor) -> None:
#_________________________________________________________________________________________
    
    cursor.execute(
        """
        INSERT INTO ledger_entries (transaction_id, wallet_id, entry_type, amount)
        VALUES (%s, %s, %s, %s)
        """,
        (transaction_id, wallet_id, entry_type, amount)
    )

#_________________________________________________________________________________________

def find_by_reference(reference: str) -> tuple | None:
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, reference, sender_wallet_id, receiver_wallet_id,
               amount, currency, type, status, created_at
        FROM transactions WHERE reference = %s
        """,
        (reference,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_by_id(transaction_id: int) -> tuple | None:
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, reference, sender_wallet_id, receiver_wallet_id,
               amount, currency, type, status, created_at
        FROM transactions WHERE id = %s
        """,
        (transaction_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_history_for_wallet(wallet_id: int, limit: int, offset: int) -> list[tuple]:
#_________________________________________________________________________________________

    """Return paginated ledger entries for a wallet joined with transaction data.
    Joins ledger_entries with transactions so each row carries both
    the entry_type (debit/credit) and the full transaction context.
    This single query gives the user everything needed to display
    a rich transaction history.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            t.id,
            t.reference,
            t.type,
            le.entry_type,
            le.amount,
            t.currency,
            t.status,
            t.created_at
        FROM ledger_entries le
        JOIN transactions t ON t.id = le.transaction_id
        WHERE le.wallet_id = %s
        ORDER BY t.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (wallet_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def count_history_for_wallet(wallet_id: int) -> int:
    """Return total number of ledger entries for a wallet (used for pagination)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM ledger_entries WHERE wallet_id = %s",
        (wallet_id,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    return total
