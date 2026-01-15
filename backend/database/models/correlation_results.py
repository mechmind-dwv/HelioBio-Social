# backend/database/models/correlation_results.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class CorrelationResult(Base):
    __tablename__ = "correlation_results"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    
    # Metadatos de la correlación
    metric_a = Column(String, nullable=False) # Ej: 'kp_index'
    metric_b = Column(String, nullable=False) # Ej: 'suicide_rate'
    correlation_type = Column(String, nullable=False) # Ej: 'pearson', 'granger', 'wavelet'
    
    # Resultados estadísticos
    r_value = Column(Float)
    p_value = Column(Float)
    lag_days = Column(Integer) # Lag óptimo en días (para Granger)
    
    # Interpretación
    interpretation = Column(String) # Ej: 'Fuerte evidencia'

    def __repr__(self):
        return f"<CorrelationResult(type='{self.correlation_type}', r='{self.r_value}', p='{self.p_value}')>"
