from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.attendance import Attendance
from ..utils.database import get_db

router = APIRouter()

@router.post("/", response_model=dict)
async def create_attendance(attendance: dict, db: Session = Depends(get_db)):
    db_attendance = Attendance(**attendance)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return {"id": db_attendance.id, "message": "Attendance created"}

@router.get("/", response_model=List[dict])
async def list_attendance(db: Session = Depends(get_db)):
    attendance_records = db.query(Attendance).all()
    return [{"id": a.id, "assignment_id": a.assignment_id, "student_id": a.student_id, "present": a.present, "notes": a.notes, "reported_by": a.reported_by, "reported_at": a.reported_at} for a in attendance_records]

@router.get("/{attendance_id}", response_model=dict)
async def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return {"id": attendance.id, "assignment_id": attendance.assignment_id, "student_id": attendance.student_id, "present": attendance.present, "notes": attendance.notes, "reported_by": attendance.reported_by, "reported_at": attendance.reported_at}

@router.put("/{attendance_id}", response_model=dict)
async def update_attendance(attendance_id: int, attendance_data: dict, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    for key, value in attendance_data.items():
        setattr(attendance, key, value)
    db.commit()
    return {"message": "Attendance updated"}

@router.delete("/{attendance_id}", response_model=dict)
async def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance deleted"}
