from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.substitute import Substitute
from ..utils.database import get_db

router = APIRouter()

@router.post("/", response_model=dict)
async def create_substitute(substitute: dict, db: Session = Depends(get_db)):
    db_substitute = Substitute(**substitute)
    db.add(db_substitute)
    db.commit()
    db.refresh(db_substitute)
    return {"id": db_substitute.id, "message": "Substitute created"}

@router.get("/", response_model=List[dict])
async def list_substitutes(db: Session = Depends(get_db)):
    substitutes = db.query(Substitute).filter(Substitute.is_active == True).all()
    return [{"id": s.id, "name": s.name, "email": s.email, "phone": s.phone, "competencies": s.competencies, "availability": s.availability, "reliability_rating": s.reliability_rating, "priority_level": s.priority_level} for s in substitutes]

@router.get("/{substitute_id}", response_model=dict)
async def get_substitute(substitute_id: int, db: Session = Depends(get_db)):
    substitute = db.query(Substitute).filter(Substitute.id == substitute_id).first()
    if not substitute:
        raise HTTPException(status_code=404, detail="Substitute not found")
    return {"id": substitute.id, "name": substitute.name, "email": substitute.email, "phone": substitute.phone, "competencies": substitute.competencies, "availability": substitute.availability, "reliability_rating": substitute.reliability_rating, "priority_level": substitute.priority_level}

@router.put("/{substitute_id}", response_model=dict)
async def update_substitute(substitute_id: int, substitute_data: dict, db: Session = Depends(get_db)):
    substitute = db.query(Substitute).filter(Substitute.id == substitute_id).first()
    if not substitute:
        raise HTTPException(status_code=404, detail="Substitute not found")
    for key, value in substitute_data.items():
        setattr(substitute, key, value)
    db.commit()
    return {"message": "Substitute updated"}

@router.delete("/{substitute_id}", response_model=dict)
async def delete_substitute(substitute_id: int, db: Session = Depends(get_db)):
    substitute = db.query(Substitute).filter(Substitute.id == substitute_id).first()
    if not substitute:
        raise HTTPException(status_code=404, detail="Substitute not found")
    substitute.is_active = False
    db.commit()
    return {"message": "Substitute deactivated"}
