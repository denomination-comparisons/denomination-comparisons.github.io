from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from .base import Base

class Substitute(Base):
    __tablename__ = "substitutes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    competencies = Column(Text)  # JSON string of subjects
    availability = Column(Text)  # JSON string of availability
    reliability_rating = Column(Float, default=0.0)
    priority_level = Column(Integer, default=2)  # 1: proven, 2: new, 3: agency
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
