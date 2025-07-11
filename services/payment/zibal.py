from .base import BasePaymentProvider
from core.config import settings
import aiohttp
from decimal import Decimal
from typing import Dict
from utils.logger import logger

class ZibalProvider(BasePaymentProvider):
    URLS = {
        'request': 'https://gateway.zibal.ir/v1/request',
        'payment': 'https://gateway.zibal.ir/start/',
        'verify': 'https://gateway.zibal.ir/v1/verify'
    }

    def __init__(self):
        self.merchant_id = settings.ZIBAL_MERCHANT_ID
        self.api_url = self.URLS['request']
        self.payment_url = self.URLS['payment']
        self.verify_url = self.URLS['verify']
        
    async def create_payment(self, amount: Decimal, callback_url: str, user_phone: str) -> Dict:
        data = {
            "merchant": self.merchant_id,
            "amount": int(amount * 10),  # تبدیل به ریال
            "callbackUrl": callback_url,
            "description": "شارژ کیف پول",
            "mobile": user_phone,
            "orderId": None  # می‌تونید یک شناسه سفارش اختصاص بدید
        }
        
        logger.info("Payment request to Zibal", extra={
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
                logger.info("Zibal response", extra={
                    "response": response.status,
                    "result": result
                })
                
                if result.get("result") == 100:
                    track_id = result["trackId"]
                    return {
                        "status": True,
                        "token": str(track_id),  # تبدیل به string برای جلوگیری از خطا
                        "url": f"{self.payment_url}{track_id}"
                    }
                
                return {
                    "status": False,
                    "message": self._get_error_message(result.get("result"))
                }
    
    async def verify_payment(self, token: str, amount: Decimal) -> Dict:
        data = {
            "merchant": self.merchant_id,
            "trackId": token
        }
        
        logger.info(f"Payment verification request to Zibal token: {token} amount: {amount}")
        
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
                logger.info(f"Zibal verification response: {str(result)}")

                if result.get("result") == 100:
                    return {
                        "status": True,
                        "ref_id": str(result.get("refNumber"))  # تبدیل به string
                    }
                
                return {
                    "status": False,
                    "message": self._get_error_message(result.get("result"))
                }

    def _get_error_message(self, error_code: int) -> str:
        """
        ترجمه کدهای خطای زیبال به پیام‌های فارسی
        """
        error_messages = {
            102: "merchant یافت نشد",
            103: "merchant غیرفعال",
            104: "merchant نامعتبر",
            201: "قبلا تایید شده",
            202: "سفارش پرداخت نشده یا ناموفق بوده است",
            203: "trackId نامعتبر است",
            -1: "خطای اعتبارسنجی",
            -2: "خطای داخلی",
            -3: "سپردن کلید تکراری",
            -4: "شناسه merchant یافت نشد",
            -5: "merchant غیرفعال",
            -6: "صحت اطلاعات ارسال شده تایید نشد",
            -7: "تراکنش قفل شده است",
            -8: "تراکنش یافت نشد",
            -9: "امکان انجام عملیات درخواستی برای این تراکنش وجود ندارد",
            -10: "مبلغ تراکنش نامعتبر است",
            -11: "مبلغ تراکنش خارج از محدوده مجاز است",
            -12: "موجودی کافی نیست",
            -13: "عملیات ناموفق"
        }
        return error_messages.get(error_code, "خطای ناشناخته در درگاه پرداخت") 