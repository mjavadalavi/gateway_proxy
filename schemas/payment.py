from pydantic import BaseModel, HttpUrl
from decimal import Decimal
from typing import Optional

class PaymentCreate(BaseModel):
    amount: Decimal
    user_phone: str
    callback_url: HttpUrl


class PaymentCreateResponse(BaseModel):
    status: bool
    token: str
    payment_url: str  # URL for redirecting to payment page 