from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.payment.proxy_payment import ProxyPaymentService
from schemas.payment import PaymentCreate, PaymentCreateResponse
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from utils.logger import logger
router = APIRouter()

@router.post("/create", response_model=PaymentCreateResponse)
async def create_payment(
    payment: PaymentCreate,
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Check if website exists with given API key"""
    payment_service = ProxyPaymentService(db)
    try:
        # Validate API key first - will raise HTTPException if invalid
        if not await payment_service.validate_api_key(x_api_key):
            logger.warning(f"Invalid API key attempt: {x_api_key}")
            raise HTTPException(status_code=403, detail="Invalid API key")
    except HTTPException:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    result = await payment_service.create_payment(
        api_key=x_api_key,
        amount=payment.amount,
        user_phone=payment.user_phone,
        callback_url=str(payment.callback_url),
        order_id=payment.order_id
    )
    return result

@router.get("/process/{gateway_token}")
async def process_payment(
    gateway_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Redirect to payment gateway"""
    payment_service = ProxyPaymentService(db)
    # Validate API key and check if transaction belongs to website
    transaction = await payment_service.transaction_repo.get_by_gateway_token(gateway_token)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    result = await payment_service.process_payment(gateway_token)
    return RedirectResponse(url=result["redirect_url"])

@router.post("/verify")
async def verify_payment(
    authority: str,
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Verify payment with gateway"""
    payment_service = ProxyPaymentService(db)
    try:
        # Validate API key first - will raise HTTPException if invalid
        if not await payment_service.validate_api_key(x_api_key):
            logger.warning(f"Invalid API key attempt: {x_api_key}")
            raise HTTPException(status_code=403, detail="Invalid API key")
    except HTTPException:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    result = await payment_service.verify_payment(
        authority=authority,
        website_token=x_api_key
    )
    return result 