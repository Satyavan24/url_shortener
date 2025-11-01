from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    original_url: str
    brand: Optional[str] = Field(None, min_length=3, max_length=10)

class URLResponse(BaseModel):
    short_url: str
    original_url: str
    admin_url: str

class URLSchema(BaseModel):
    id: int
    short_code: str
    original_url: str
    secret_key: str
    created_at: datetime
    click_count: int
    last_accessed_at: Optional[datetime]

    class Config:
        from_attributes = True