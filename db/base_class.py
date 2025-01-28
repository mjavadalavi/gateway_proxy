from typing import Any
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class Base:
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

Base = declarative_base(cls=Base) 