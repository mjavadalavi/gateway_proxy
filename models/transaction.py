from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from db.base_class import Base

class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("website.id"))
    amount = Column(Numeric(10, 2))
    status = Column(String, default="pending")  # pending, completed, failed
    ref_id = Column(String, nullable=True)
    user_phone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    callback_url = Column(String)
    gateway_token = Column(String, unique=True, nullable=True) 
    gateway_url = Column(String, nullable=True)