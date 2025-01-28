from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from .endpoints import payments, transactions


api_router = APIRouter()

api_router.mount("/static", StaticFiles(directory="static"), name="static") 


api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"]) 