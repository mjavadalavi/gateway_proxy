from sqlalchemy import create_engine
from core.config import settings
from .base_class import Base
from models.transaction import Transaction


def init_db():
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine) 