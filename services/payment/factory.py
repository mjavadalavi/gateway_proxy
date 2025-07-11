from core.config import settings
from .base import BasePaymentProvider
from .zarinpal import ZarinpalProvider
from .zibal import ZibalProvider

def get_payment_provider() -> BasePaymentProvider:
    providers = {
        "zarinpal": ZarinpalProvider,
        'zibal': ZibalProvider
    }
    
    provider_class = providers.get(settings.PAYMENT_GATEWAY)
    if not provider_class:
        raise ValueError(f"Payment gateway {settings.PAYMENT_GATEWAY} not supported")
    
    return provider_class() 