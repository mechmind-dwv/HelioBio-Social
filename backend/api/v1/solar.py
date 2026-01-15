# backend/api/v1/solar.py
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Definición del modelo de respuesta
class SolarActivity(BaseModel):
    kp_index: float
    sunspot_number: int
    solar_wind_speed: float
    timestamp: datetime
    alert_level: str

@router.get("/current", response_model=SolarActivity, summary="Obtener la actividad solar actual")
def get_current_solar_activity():
    """
    Simula la obtención de los datos de actividad solar en tiempo real.
    """
    # Datos simulados basados en el ejemplo del README
    simulated_data = {
        "kp_index": 7.0,
        "sunspot_number": 145,
        "solar_wind_speed": 650.0,
        "timestamp": datetime.now(),
        "alert_level": "FUERTE"
    }
    return simulated_data

@router.get("/historical", summary="Obtener datos históricos de actividad solar")
def get_historical_solar_activity(start_date: str, end_date: str):
    """
    Simula la obtención de datos históricos de actividad solar en un rango de fechas.
    """
    return {
        "message": "Endpoint de datos históricos simulado",
        "start": start_date,
        "end": end_date,
        "count": 1000,
        "data_source": "NOAA SWPC/NCEI"
    }
