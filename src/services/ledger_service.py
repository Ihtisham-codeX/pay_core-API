from src.repositories import wallet_repository, transaction_repository
from src.exceptions.handlers import WalletNotFoundException
from src.database.connection import conn


# an integrity check that verifies wallet.balance matches ledger totals.


_MINOR_UNIT_DIVISOR = 100

#_________________________________________________________________________________________

def get_ledger(user_id: int) -> dict:
#_________________________________________________________________________________________

    """Return all ledger entries for the authenticated user's wallet."""
    wallet_row = wallet_repository.find_by_user_id(user_id)
    if wallet_row is None:
        raise WalletNotFoundException()

    wallet_id = wallet_row[0]

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            le.id,
            le.entry_type,
            le.amount,
            t.reference,
            t.currency,
            t.created_at
        FROM ledger_entries le
        JOIN transactions t ON t.id = le.transaction_id
        WHERE le.wallet_id = %s
        ORDER BY le.created_at DESC
        """,
        (wallet_id,)
    )
    rows = cursor.fetchall()
    cursor.close()

    entries = []
    for row in rows:
        amount_major = row[2] / _MINOR_UNIT_DIVISOR
        entries.append({
            "id":         row[0],
            "entry_type": row[1],
            "amount":     -amount_major if row[1] == "debit" else amount_major,
            "reference":  row[3],
            "currency":   row[4],
            "created_at": row[5],
        })

    return {
        "wallet_id":     wallet_id,
        "total_entries": len(entries),
        "entries":       entries,
    }

#_________________________________________________________________________________________

def verify_balance_integrity(user_id: int) -> dict:
#_________________________________________________________________________________________

    """Verify that the wallet balance matches the sum of ledger entries"""
    wallet_row = wallet_repository.find_by_user_id(user_id)
    if wallet_row is None:
        raise WalletNotFoundException()

    wallet_id       = wallet_row[0]
    wallet_balance  = wallet_row[2]   # stored minor units

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN entry_type = 'credit' THEN amount ELSE 0 END), 0) AS total_credits,
            COALESCE(SUM(CASE WHEN entry_type = 'debit'  THEN amount ELSE 0 END), 0) AS total_debits
        FROM ledger_entries
        WHERE wallet_id = %s
        """,
        (wallet_id,)
    )
    row = cursor.fetchone()
    cursor.close()

    total_credits  = row[0]
    total_debits   = row[1]
    ledger_balance = total_credits - total_debits

    return {
        "wallet_id":      wallet_id,
        "wallet_balance": wallet_balance  / _MINOR_UNIT_DIVISOR,
        "ledger_balance": ledger_balance  / _MINOR_UNIT_DIVISOR,
        "total_credits":  total_credits   / _MINOR_UNIT_DIVISOR,
        "total_debits":   total_debits    / _MINOR_UNIT_DIVISOR,
        "integrity_ok":   wallet_balance == ledger_balance,
    }
