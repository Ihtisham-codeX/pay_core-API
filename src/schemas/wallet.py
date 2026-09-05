from pydantic import BaseModel
from datetime import datetime


class WalletResponse(BaseModel):
    """Public wallet view.
    Balance is returned in the MAJOR unit (e.g. 1000.50 PKR),
    but stored internally as INTEGER minor units (e.g. 100050 paisa).
    """
    id:         int
    user_id:    int
    balance:    float       # converted from minor units to display units/major units
    currency:   str
    status:     str
    created_at: datetime
    updated_at: datetime
