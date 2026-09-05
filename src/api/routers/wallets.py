from fastapi import APIRouter, Depends
from src.schemas.wallet        import WalletResponse
from src.services              import wallet_service
from src.security.dependencies import get_current_user



router = APIRouter(prefix="/wallets", tags=["Wallets"])

#_________________________________________________________________________________________

@router.get("/me", response_model=WalletResponse)
#_________________________________________________________________________________________

def get_my_wallet(user: dict = Depends(get_current_user)):
    """
    Return the full wallet of the authenticated user.

    Workflow:
      JWT payload → extract user_id → wallet_service.get_wallet()
      → WalletResponse (balance in major units, e.g. PKR)
    """
    return wallet_service.get_wallet(user_id=user["user_id"])

#_________________________________________________________________________________________

@router.get("/me/balance")
#_________________________________________________________________________________________

def get_my_balance(user: dict = Depends(get_current_user)):
    """
    Lightweight endpoint — return only balance and currency.
    Useful for mobile clients that need to display balance without
    fetching the full wallet object.
    """
    return wallet_service.get_wallet_balance(user_id=user["user_id"])
