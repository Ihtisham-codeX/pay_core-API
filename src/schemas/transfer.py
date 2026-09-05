from pydantic import BaseModel, field_validator
from datetime import datetime




class TransferRequest(BaseModel):
    receiver_username: str
    amount: float                # client sends in major units (e.g. 500.00 PKR)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v


class TransferResponse(BaseModel):
    reference:          str
    amount:             float    # returned in major units
    currency:           str
    status:             str
    sender_wallet_id:   int
    receiver_wallet_id: int
    created_at:         datetime
