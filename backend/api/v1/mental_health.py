# backend/api/v1/mental_health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from database.models.mental_health_data import MentalHealthData, MentalHealthSummary

router = APIRouter()

# Schemas Pydantic
class MentalHealthDataCreate(BaseModel):
    region: str
    psychiatric_admissions: int | None = None
    suicide_rate: float | None = None
    bipolar_episodes: int | None = None
    depression_index: float | None = None

class MentalHealthDataResponse(BaseModel):
    time: datetime
    region: str
    psychiatric_admissions: int | None
    suicide_rate: float | None
    bipolar_episodes: int | None
    depression_index: float | None
    
    class Config:
        from_attributes = True

# Endpoints
@router.get("/", response_model=List[MentalHealthDataResponse])
def get_mental_health_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene datos de salud mental"""
    data = db.query(MentalHealthData).offset(skip).limit(limit).all()
    return data

@router.post("/", response_model=MentalHealthDataResponse)
def create_mental_health_data(
    data: MentalHealthDataCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo registro de salud mental"""
    db_data = MentalHealthData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """Obtiene el resumen global de salud mental"""
    summary = db.query(MentalHealthSummary).order_by(
        MentalHealthSummary.date.desc()
    ).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="No hay datos de resumen")
    
    return summary
