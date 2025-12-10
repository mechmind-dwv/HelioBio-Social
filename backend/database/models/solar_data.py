# backend/database/models/solar_data.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class SolarData(Base):
    __tablename__ = "solar_data"

    # La columna 'time' es la clave de tiempo para TimescaleDB
    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())
    kp_index = Column(Float)
    sunspot_number = Column(Integer)
    solar_wind_speed = Column(Float) # km/s
    proton_density = Column(Float) # partículas/cm³
    cme_flag = Column(Integer, default=0) # 1 si hay Eyección de Masa Coronal

    def __repr__(self):
        return f"<SolarData(time='{self.time}', kp_index='{self.kp_index}')>"
