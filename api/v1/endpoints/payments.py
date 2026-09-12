from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from fastapi.responses import RedirectResponse
from repositories.transaction import TransactionRepository
from utils.logger import logger
from core.config import settings
from utils.urls import append_query_parameters
router = APIRouter()

@router.get("/callback")
async def payment_callback(
    Authority: str,
    Status: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle gateway callback"""
    try:
        transaction_repo = TransactionRepository(db)
        transaction = await transaction_repo.get_by_gateway_token(Authority)
        
        if not transaction:
            logger.error("Transaction not found for payment callback")
            return RedirectResponse(url=f"{settings.ERROR_REDIRECT_URL}")

        callback_url = transaction.callback_url
        
        if Status == "OK":
            logger.info("Successful payment callback")
            return RedirectResponse(
                url=append_query_parameters(
                    callback_url,
                    Authority=Authority,
                    Status="OK",
                )
            )
        else:
            logger.warning("Failed payment callback")
            return RedirectResponse(
                url=append_query_parameters(
                    callback_url,
                    Authority=Authority,
                    Status="NOK",
                )
            )

    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return RedirectResponse(url=f"{settings.ERROR_REDIRECT_URL}")
