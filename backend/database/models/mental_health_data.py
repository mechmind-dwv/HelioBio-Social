# backend/database/models/mental_health_data.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class MentalHealthData(Base):
    __tablename__ = "mental_health_data"

    # La columna 'time' es la clave de tiempo para TimescaleDB
    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())
    region = Column(String, nullable=False)
    psychiatric_admissions = Column(Integer)
    suicide_rate = Column(Float) # Por 100k habitantes
    bipolar_episodes = Column(Integer)
    depression_index = Column(Float) # Escala 0-100

    def __repr__(self):
        return f"<MentalHealthData(time='{self.time}', region='{self.region}', admissions='{self.psychiatric_admissions}')>"

class MentalHealthSummary(Base):
    __tablename__ = "mental_health_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), default=func.now())
    global_depression_index = Column(Float)
    global_suicide_rate = Column(Float)
    
    def __repr__(self):
        return f"<MentalHealthSummary(date='{self.date}', index='{self.global_depression_index}')>"
