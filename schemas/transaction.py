from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: Decimal
    order_id: str
    user_phone: str
    status: str
    ref_id: Optional[str] = None
    
class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    website_id: int
    token: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TransactionStats(BaseModel):
    total_amount: Decimal
    status_counts: dict[str, int] 