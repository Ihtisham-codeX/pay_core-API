from src.repositories import wallet_repository
from src.schemas.wallet  import WalletResponse
from src.exceptions.handlers import WalletNotFoundException


_MINOR_UNIT_DIVISOR = 100   # 1 PKR = 100 paisa

#_________________________________________________________________________________________

def _row_to_wallet_response(row: tuple) -> WalletResponse:
#_________________________________________________________________________________________

    """Map a raw DB tuple to a WalletResponse schema.
    Column order must match the SELECT in wallet_repository.
    """
    return WalletResponse(
        id         = row[0],
        user_id    = row[1],
        balance    = row[2] / _MINOR_UNIT_DIVISOR,   # minor → major units
        currency   = row[3],
        status     = row[4],
        created_at = row[5],
        updated_at = row[6],
    )

#_________________________________________________________________________________________

def get_wallet(user_id: int) -> WalletResponse:
#_________________________________________________________________________________________

    """Return the wallet belonging to the authenticated user."""
    row = wallet_repository.find_by_user_id(user_id)
    if row is None:
        raise WalletNotFoundException()
    return _row_to_wallet_response(row)

#_________________________________________________________________________________________

def get_wallet_balance(user_id: int) -> dict:
#_________________________________________________________________________________________

    """Return only the balance and currency — lightweight endpoint for Stage 2 clients."""
    row = wallet_repository.find_by_user_id(user_id)
    if row is None:
        raise WalletNotFoundException()
    return {
        "balance":  row[2] / _MINOR_UNIT_DIVISOR,
        "currency": row[3],
    }
