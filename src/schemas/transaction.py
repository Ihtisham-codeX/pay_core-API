from pydantic import BaseModel
from datetime import datetime


class TransactionResponse(BaseModel):
    """A single transaction record as seen by the authenticated user.
    `entry_type` tells the user whether this was money going OUT (debit)
    or coming IN (credit) for their wallet specifically.
    `amount` is signed: negative for debits, positive for credits.
    """
    id:             int
    reference:      str
    type:           str
    entry_type:     str     # 'debit' | 'credit' (relative to the requesting user)
    amount:         float   # negative = sent, positive = received
    currency:       str
    status:         str
    created_at:     datetime


class TransactionListResponse(BaseModel):
    """Paginated transaction history."""
    total:        int
    page:         int
    page_size:    int
    transactions: list[TransactionResponse]
