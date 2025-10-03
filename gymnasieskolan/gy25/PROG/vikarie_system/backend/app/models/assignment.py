from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String, index=True)  # External lesson ID
    subject = Column(String)
    class_name = Column(String)
    room = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    teacher_notes = Column(Text)
    substitute_id = Column(Integer, ForeignKey("substitutes.id"))
    status = Column(String, default="pending")  # pending, accepted, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
