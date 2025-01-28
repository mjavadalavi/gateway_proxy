from core.config import settings
from .base import BasePaymentProvider
from .zarinpal import ZarinpalProvider

def get_payment_provider() -> BasePaymentProvider:
    providers = {
        "zarinpal": ZarinpalProvider
    }
    
    provider_class = providers.get(settings.PAYMENT_GATEWAY)
    if not provider_class:
        raise ValueError(f"Payment gateway {settings.PAYMENT_GATEWAY} not supported")
    
    return provider_class() 