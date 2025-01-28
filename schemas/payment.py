from pydantic import BaseModel, HttpUrl
from decimal import Decimal
from typing import Optional

class PaymentCreate(BaseModel):
    amount: Decimal
    user_phone: str
    callback_url: HttpUrl
    order_id: str


class PaymentCreateResponse(BaseModel):
    status: bool
    payment_url: str  # URL for redirecting to payment page 