from fastapi import HTTPException
from repositories.website import WebsiteRepository
from repositories.transaction import TransactionRepository
from decimal import Decimal
from typing import Dict
from urllib.parse import urlparse
from utils.logger import logger
from core.config import settings
import traceback
from services.payment.factory import get_payment_provider

class ProxyPaymentService:
    def __init__(self, db_session):
        self.db = db_session
        self.website_repo = WebsiteRepository(db_session)
        self.transaction_repo = TransactionRepository(db_session)
        self.payment_provider = get_payment_provider()
    
    async def validate_api_key(self, api_key: str):
        website = await self.website_repo.get_by_api_key(api_key)
        if not website:
            logger.warning(f"Invalid API key attempt: {api_key}")
            raise HTTPException(status_code=403, detail="Invalid API key")
        return website

    def validate_callback_url(self, website, callback_url: str) -> bool:
        try:
            callback_domain = urlparse(callback_url).netloc
            logger.info(f"Callback: {callback_domain}, {website.domain}")
            return callback_domain == website.domain
        except Exception as e:
            logger.error(f"Callback URL validation error: {str(e)}")
            return False

    async def create_payment(self, api_key: str, amount: Decimal, user_phone: str, callback_url: str) -> Dict:
        """Create payment and get gateway token"""
        try:
            website = await self.validate_api_key(api_key)
            
            if not self.validate_callback_url(website, callback_url):
                logger.warning(f"Invalid callback URL attempt: {callback_url} for website: {website.id}")
                raise HTTPException(status_code=400, detail="Invalid callback URL")

            # Create payment in gateway first
            payment_result = await self.payment_provider.create_payment(
                amount=amount,
                callback_url=f"{settings.BASE_URL}/gateway/callback",
                user_phone=user_phone
            )
            logger.info(f"payment: {payment_result}")

            if not payment_result["status"]:
                logger.error(f"Gateway payment creation failed: {payment_result}")
                raise HTTPException(status_code=500, detail="Gateway payment failed")

            # Generate unique token and save transaction
            await self.transaction_repo.create(
                amount=amount,
                website_id=website.id,
                user_phone=user_phone,
                callback_url=callback_url,
                gateway_token=payment_result["token"],
                gateway_url=payment_result["url"]
            )

            logger.info(f"Created payment request: {payment_result['token']} for website: {website.id}")
            
            return {
                "status": True,
                "token": payment_result['token'],
                "payment_url": f"{settings.BASE_URL}/payments/process/{payment_result['token']}"
            }

        except HTTPException as http_ex:
            raise http_ex

        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            raise HTTPException(status_code=500, detail="Payment creation failed")

    async def process_payment(self, gateway_token: str) -> Dict:
        """Get payment URL for redirect"""
        try:
            transaction = await self.transaction_repo.get_by_gateway_token(gateway_token)
            if not transaction:
                logger.warning(f"Invalid payment token attempt: {gateway_token}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Just return the gateway URL with authority
            return {
                "redirect_url": transaction.gateway_url
            }

        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            raise HTTPException(status_code=500, detail="Payment processing failed")

    async def verify_payment(self, authority: str, website_token: str) -> Dict:
        """Verify payment with gateway"""
        try:
            website = await self.validate_api_key(website_token)
            transaction = await self.transaction_repo.get_by_gateway_token(authority)
            
            if not transaction:
                logger.warning(f"Invalid authority in verify: {authority}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            if transaction.website_id != website.id:
                logger.warning(f"Website mismatch in verify. Expected: {transaction.website_id}, Got: {website.id}")
                raise HTTPException(status_code=403, detail="Invalid website token")

            verify_result = await self.payment_provider.verify_payment(authority, transaction.amount)

            if verify_result["status"]:
                await self.transaction_repo.update_status(
                    token=authority,
                    status="completed",
                    ref_id=verify_result["ref_id"]
                )
                logger.info(f"Payment verified successfully: {authority}")
            else:
                await self.transaction_repo.update_status(
                    token=authority,
                    status="failed"
                )
                logger.warning(f"Payment verification failed: {authority}")

            return verify_result

        except Exception as e:
            logger.error(f"Payment verification error: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Payment verification failed") 