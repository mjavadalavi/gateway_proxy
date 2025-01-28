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
            "amount": int(amount * 10),  # تبدیل به ریال
            "callback_url": callback_url,
            "description": "شارژ کیف پول",
            "metadata": {
                "mobile": user_phone
            }
        }
        
        logger.info(f"Payment request to Zarinpal (sandbox: {self.is_sandbox})", extra={
            "api_url": self.api_url,
            "data": data
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
                logger.info(f"Zarinpal response", extra={"response": result})
                
                if result.get("data", {}).get("code") == 100:
                    authority = result["data"]["authority"]
                    return {
                        "status": True,
                        "token": authority,
                        "url": f"{self.payment_url}{authority}"
                    }
                
                return {
                    "status": False,
                    "message": result.get("errors", {}).get("message", "خطا در اتصال به درگاه پرداخت")
                }
    
    async def verify_payment(self, token: str, amount) -> Dict:
        data = {
            "merchant_id": self.merchant_id,
            "authority": token,
            "amount": int(amount) * 10
        }
        
        logger.info(f"Payment verification request to Zarinpal: {str(data)}")
        
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
                logger.info(f"Zarinpal verification response: {str(result)}")
                
                if result.get("data", {}).get("code") == 100:
                    return {
                        "status": True,
                        "ref_id": result["data"].get("ref_id")
                    }

                if result.get("data", {}).get("code") == 101:
                    return {
                        "status": False,
                        "ref_id": result["data"].get("ref_id")
                    }

                return {
                    "status": False,
                    "message": result.get("errors", {}).get("message", "خطا در تایید پرداخت")
                } 