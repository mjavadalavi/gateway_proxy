from .base import BasePaymentProvider
from core.config import settings
import aiohttp
from decimal import Decimal
from typing import Dict
from utils.logger import logger

class ZarinpalProvider(BasePaymentProvider):
    URLS = {
        'sandbox': {
            'request': 'https://sandbox.zarinpal.com/pg/v4/payment/request.json',
            'payment': 'https://sandbox.zarinpal.com/pg/StartPay/',
            'verify': 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
        },
        'production': {
            'request': 'https://api.zarinpal.com/pg/v4/payment/request.json',
            'payment': 'https://www.zarinpal.com/pg/StartPay/',
            'verify': 'https://api.zarinpal.com/pg/v4/payment/verify.json'
        }
    }

    def __init__(self):
        self.is_sandbox = settings.PAYMENT_ENV == 'sandbox'
        self.merchant_id = (
            '1344b5d4-0048-11e8-94db-005056a205be' 
            if self.is_sandbox 
            else settings.ZARINPAL_MERCHANT_ID
        )
        env = 'sandbox' if self.is_sandbox else 'production'
        self.api_url = self.URLS[env]['request']
        self.payment_url = self.URLS[env]['payment']
        self.verify_url = self.URLS[env]['verify']
        
    async def create_payment(self, amount: Decimal, callback_url: str, user_phone: str) -> Dict:
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),  # تبدیل به ریال
            "callback_url": callback_url,
            "description": "شارژ کیف پول",
            "metadata": {
                "mobile": user_phone
            }
        }
        
        logger.info("Payment request to Zarinpal", extra={
            "sandbox": self.is_sandbox,
            "api_url": self.api_url,
            "amount": data["amount"],
        })
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            ) as response:
                result = await response.json()
                data_result = result.get("data")
                data_result = data_result if isinstance(data_result, dict) else {}
                error_result = result.get("errors")
                error_result = error_result if isinstance(error_result, dict) else {}
                logger.info(
                    "Zarinpal payment response",
                    extra={
                        "http_status": response.status,
                        "code": data_result.get("code") or error_result.get("code"),
                    },
                )
                
                if data_result.get("code") == 100:
                    authority = data_result["authority"]
                    return {
                        "status": True,
                        "token": authority,
                        "url": f"{self.payment_url}{authority}"
                    }
                
                return {
                    "status": False,
                    "message": error_result.get(
                        "message",
                        "خطا در اتصال به درگاه پرداخت",
                    ),
                }
    
    async def verify_payment(self, token: str, amount) -> Dict:
        data = {
            "merchant_id": self.merchant_id,
            "authority": token,
            "amount": int(amount)
        }
        
        logger.info("Payment verification request to Zarinpal")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.verify_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            ) as response:
                result = await response.json()
                data_result = result.get("data")
                data_result = data_result if isinstance(data_result, dict) else {}
                error_result = result.get("errors")
                error_result = error_result if isinstance(error_result, dict) else {}
                logger.info(
                    "Zarinpal verification response",
                    extra={
                        "http_status": response.status,
                        "code": data_result.get("code") or error_result.get("code"),
                    },
                )
                
                if data_result.get("code") == 100:
                    return {
                        "status": True,
                        "ref_id": data_result.get("ref_id")
                    }

                if data_result.get("code") == 101:
                    return {
                        "status": False,
                        "ref_id": data_result.get("ref_id")
                    }

                return {
                    "status": False,
                    "message": error_result.get(
                        "message",
                        "خطا در تایید پرداخت",
                    ),
                }
