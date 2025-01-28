from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.init_db import init_db
import logging
from api.v1.endpoints import payments, proxy_payment
from utils.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(payments.router, prefix="/gateway", tags=["gateway"])
app.include_router(proxy_payment.router, prefix="/payments", tags=["payments"]) 

# Add database to app state
@app.on_event("startup")
async def startup():
    try:
        # Initialize database
        init_db()
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Error in startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    try:
        # Close database connection
        if hasattr(app.state, "db"):
            await app.state.db.close()
        
    except Exception as e:
        logger.error(f"Error in shutdown: {str(e)}")

@app.get("/")
def read_root():
    return {"Hello": "World"} 