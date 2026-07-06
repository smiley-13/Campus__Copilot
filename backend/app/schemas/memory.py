from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class MemoryBase(BaseModel):
    key: str = Field(..., description="The context key, e.g., 'branch'")
    value: str = Field(..., description="The value of the memory")
    category: Optional[str] = Field(default="general")
    priority: Optional[str] = Field(default="low")
    source: Optional[str] = Field(default="chat")
    confidence: Optional[float] = Field(default=1.0)
    metadata_json: Optional[str] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    value: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    metadata_json: Optional[str] = None

class MemoryRead(MemoryBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_accessed: Optional[datetime]

    class Config:
        from_attributes = True
