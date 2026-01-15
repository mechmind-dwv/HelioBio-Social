import sys
from pathlib import Path
backend_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_path))

from database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    mental_health_records = relationship("MentalHealthData", back_populates="user")
    solar_data_records = relationship("SolarData", back_populates="user")

class MentalHealthData(Base):
    __tablename__ = "mental_health_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Float, nullable=False)  # 1-10
    energy_level = Column(Float, nullable=False)  # 1-10
    sleep_quality = Column(Float)  # 1-10
    stress_level = Column(Float)  # 1-10
    notes = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="mental_health_records")

class SolarData(Base):
    __tablename__ = "solar_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    solar_irradiance = Column(Float)  # W/m²
    sunlight_hours = Column(Float)  # horas
    uv_index = Column(Float)
    location_lat = Column(Float)
    location_lon = Column(Float)
    
    # Relaciones
    user = relationship("User", back_populates="solar_data_records")
