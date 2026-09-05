from fastapi import APIRouter, Depends
from src.schemas.transfer      import TransferRequest, TransferResponse
from src.services              import transfer_service
from src.security.dependencies import get_current_user


# ─── Transfers Router ─────────────────────────────────────────────────────────
# A transfer is an atomic movement of money between two wallets.
# The router only wires the request to the service — all logic lives in
# transfer_service.execute_transfer().


router = APIRouter(prefix="/transfers", tags=["Transfers"])

#_________________________________________________________________________________________

@router.post("/", response_model=TransferResponse, status_code=201)
#_________________________________________________________________________________________

def create_transfer(body: TransferRequest, user: dict = Depends(get_current_user)):
    """
    Send money to another user.

    Workflow:
      TransferRequest (receiver_username + amount) →
      transfer_service.execute_transfer() →
      atomic DB transaction (lock → validate → debit → credit → ledger) →
      TransferResponse (reference, amount, status)
    """
    return transfer_service.execute_transfer(
        sender_user_id    = user["user_id"],
        receiver_username = body.receiver_username,
        amount_major      = body.amount,
    )
