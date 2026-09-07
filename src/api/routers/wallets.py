from fastapi import APIRouter, Depends
from src.schemas.wallet        import WalletResponse
from src.services              import wallet_service, ledger_service
from src.security.dependencies import get_current_user


router = APIRouter(prefix="/wallets", tags=["Wallets"])

#_________________________________________________________________________________________

@router.get("/me", response_model=WalletResponse)
#_________________________________________________________________________________________

def get_my_wallet(user: dict = Depends(get_current_user)):

    return wallet_service.get_wallet(user_id=user["user_id"])

#_________________________________________________________________________________________

@router.get("/me/balance")
#_________________________________________________________________________________________

def get_my_balance(user: dict = Depends(get_current_user)):

    return wallet_service.get_wallet_balance(user_id=user["user_id"])


#_________________________________________________________________________________________

@router.get("/me/ledger")
#_________________________________________________________________________________________

def get_my_ledger(user: dict = Depends(get_current_user)):

    return ledger_service.get_ledger(user_id=user["user_id"])

#_________________________________________________________________________________________

@router.get("/me/ledger/verify")
#_________________________________________________________________________________________

def verify_my_balance(user: dict = Depends(get_current_user)):
    """
    Returns:
      wallet_balance  — what wallets.balance currently shows
      ledger_balance  — what the ledger entries sum to
      integrity_ok    — True if they match (they always should)
    If integrity_ok is False, there is a data consistency bug somewhere.
    """
    return ledger_service.verify_balance_integrity(user_id=user["user_id"])

