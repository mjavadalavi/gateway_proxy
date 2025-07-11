from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gateway Proxy"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    #PORTS
    ADMINER_PORT: int
    WEB_PORT: int

    HOST: str = "0.0.0.0"
    SOURCE_COMMIT: str = '7d5b2b82dc95340f35f7ec64a869e28acafb5db6'

    # Payment Gateway
    PAYMENT_GATEWAY: str = "zarinpal"
    ZARINPAL_MERCHANT_ID: str
    PAYMENT_ENV: str = "sandbox"
    PAYMENT_CALLBACK: str = "https://pay.roblit.ir/payment/callback"
    ZARINPAL_GATEWAY_URL: str = "https://www.zarinpal.com/pg/StartPay/"
    ZIBAL_MERCHANT_ID: str

    # Application
    BASE_URL: str = "https://pay.example.com"
    ERROR_REDIRECT_URL: str = "https://pay.example.com/error"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 