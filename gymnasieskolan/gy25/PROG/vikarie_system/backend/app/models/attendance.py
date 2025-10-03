from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from .base import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(String)  # External student ID
    present = Column(Boolean)
    notes = Column(Text)
    reported_by = Column(Integer, ForeignKey("substitutes.id"))
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
