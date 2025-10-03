from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.assignment import Assignment
from ..utils.database import get_db

router = APIRouter()

@router.post("/", response_model=dict)
async def create_assignment(assignment: dict, db: Session = Depends(get_db)):
    db_assignment = Assignment(**assignment)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return {"id": db_assignment.id, "message": "Assignment created"}

@router.get("/", response_model=List[dict])
async def list_assignments(db: Session = Depends(get_db)):
    assignments = db.query(Assignment).all()
    return [{"id": a.id, "lesson_id": a.lesson_id, "subject": a.subject, "class_name": a.class_name, "room": a.room, "start_time": a.start_time, "end_time": a.end_time, "teacher_notes": a.teacher_notes, "substitute_id": a.substitute_id, "status": a.status} for a in assignments]

@router.get("/{assignment_id}", response_model=dict)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"id": assignment.id, "lesson_id": assignment.lesson_id, "subject": assignment.subject, "class_name": assignment.class_name, "room": assignment.room, "start_time": assignment.start_time, "end_time": assignment.end_time, "teacher_notes": assignment.teacher_notes, "substitute_id": assignment.substitute_id, "status": assignment.status}

@router.put("/{assignment_id}", response_model=dict)
async def update_assignment(assignment_id: int, assignment_data: dict, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    for key, value in assignment_data.items():
        setattr(assignment, key, value)
    db.commit()
    return {"message": "Assignment updated"}

@router.delete("/{assignment_id}", response_model=dict)
async def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted"}
