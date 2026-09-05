from src.repositories import wallet_repository
from src.schemas.wallet  import WalletResponse
from src.exceptions.handlers import WalletNotFoundException


# Balance Unit Conversion:
#   The DB stores balance as INTEGER minor units (paisa).
#   The API returns balance as a float in major units (PKR).
#   Example: DB stores 150000 → API returns 1500.00



_MINOR_UNIT_DIVISOR = 100   # 1 PKR = 100 paisa


def _row_to_wallet_response(row: tuple) -> WalletResponse:
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


def get_wallet(user_id: int) -> WalletResponse:
    """Return the wallet belonging to the authenticated user."""
    row = wallet_repository.find_by_user_id(user_id)
    if row is None:
        raise WalletNotFoundException()
    return _row_to_wallet_response(row)


def get_wallet_balance(user_id: int) -> dict:
    """Return only the balance and currency — lightweight endpoint for Stage 2 clients."""
    row = wallet_repository.find_by_user_id(user_id)
    if row is None:
        raise WalletNotFoundException()
    return {
        "balance":  row[2] / _MINOR_UNIT_DIVISOR,
        "currency": row[3],
    }
