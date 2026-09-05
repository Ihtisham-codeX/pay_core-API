from src.repositories import transaction_repository, wallet_repository
from src.schemas.transaction import TransactionResponse, TransactionListResponse
from src.exceptions.handlers import WalletNotFoundException



_MINOR_UNIT_DIVISOR = 100

#_________________________________________________________________________________________

def _row_to_transaction_response(row: tuple) -> TransactionResponse:
#_________________________________________________________________________________________

    """Map a raw ledger+transaction JOIN row to a TransactionResponse.
    Column order from find_history_for_wallet():
      0: t.id
      1: t.reference
      2: t.type
      3: le.entry_type  ('debit' | 'credit')
      4: le.amount      (minor units)
      5: t.currency
      6: t.status
      7: t.created_at
    """
    entry_type = row[3]
    amount_major = row[4] / _MINOR_UNIT_DIVISOR

    # Negative = money left your wallet (debit)
    # Positive = money entered your wallet (credit)
    signed_amount = -amount_major if entry_type == "debit" else amount_major

    return TransactionResponse(
        id         = row[0],
        reference  = row[1],
        type       = row[2],
        entry_type = entry_type,
        amount     = signed_amount,
        currency   = row[5],
        status     = row[6],
        created_at = row[7],
    )

#_________________________________________________________________________________________

def get_history(user_id: int, page: int, page_size: int) -> TransactionListResponse:
#_________________________________________________________________________________________

    """Return paginated transaction history for the authenticated user.
    Uses the ledger_entries table so the user sees every event
    that touched their wallet - whether they were sender or receiver.
    """
    wallet_row = wallet_repository.find_by_user_id(user_id)
    if wallet_row is None:
        raise WalletNotFoundException()

    wallet_id = wallet_row[0]
    offset    = (page - 1) * page_size

    rows  = transaction_repository.find_history_for_wallet(wallet_id, limit=page_size, offset=offset)
    total = transaction_repository.count_history_for_wallet(wallet_id)

    return TransactionListResponse(
        total        = total,
        page         = page,
        page_size    = page_size,
        transactions = [_row_to_transaction_response(row) for row in rows],
    )
