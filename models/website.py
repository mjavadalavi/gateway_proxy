from sqlalchemy import Column, Integer, String, Boolean, ARRAY
from db.base_class import Base

class Website(Base):
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)