from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    key = Column(String, index=True, nullable=False)
    value = Column(String, nullable=False)
    category = Column(String, index=True, nullable=True)
    priority = Column(String, default="low") # high, medium, low
    source = Column(String, default="chat") # chat, document, manual, etc.
    confidence = Column(Float, default=1.0) # 0.0 to 1.0
    metadata_json = Column(Text, nullable=True) # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
