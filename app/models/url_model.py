from sqlalchemy import Column, Integer, String, DateTime, func
from app.connection.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    click_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True, default=None)