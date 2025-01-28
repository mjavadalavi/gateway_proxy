from abc import ABC, abstractmethod
from typing import Optional, Dict
from decimal import Decimal

class BasePaymentProvider(ABC):
    @abstractmethod
    async def create_payment(self, amount: Decimal, callback_url: str) -> Dict:
        """Create payment and return payment URL"""
        pass
    
    @abstractmethod
    async def verify_payment(self, token: str) -> Dict:
        """Verify payment and return transaction details"""
        pass 