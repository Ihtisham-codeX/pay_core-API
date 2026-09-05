from fastapi import APIRouter, Depends, Query
from src.schemas.transaction   import TransactionListResponse
from src.services              import transaction_service
from src.security.dependencies import get_current_user



router = APIRouter(prefix="/transactions", tags=["Transactions"])

#_________________________________________________________________________________________

@router.get("/", response_model=TransactionListResponse)
#_________________________________________________________________________________________

def get_my_transactions(
    user:      dict = Depends(get_current_user),
    page:      int  = Query(default=1,  ge=1,  description="Page number"),
    page_size: int  = Query(default=10, ge=1, le=100, description="Results per page"),
):
    """
    Return the paginated transaction history for the authenticated user.

    Reads from the ledger_entries table so both sent and received
    transactions appear. Amounts are signed:
      Negative → you sent money (debit)
      Positive → you received money (credit)

    Query params:
      ?page=1&page_size=10
    """
    return transaction_service.get_history(
        user_id   = user["user_id"],
        page      = page,
        page_size = page_size,
    )
