# backend/api/v1/mental_health.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List

router = APIRouter()

# Definición del modelo de respuesta (similar al ejemplo del README)
class MentalHealthData(BaseModel):
    region: str
    date: date
    psychiatric_admissions: int
    suicide_rate: float
    bipolar_episodes: int
    depression_index: float

# Simulación de datos
SIMULATED_DATA = [
    {
      "region": "Europe",
      "date": date(2025, 3, 15),
      "psychiatric_admissions": 1247,
      "suicide_rate": 12.3,
      "bipolar_episodes": 89,
      "depression_index": 67.2
    },
    {
      "region": "USA",
      "date": date(2025, 3, 15),
      "psychiatric_admissions": 850,
      "suicide_rate": 14.5,
      "bipolar_episodes": 60,
      "depression_index": 71.0
    }
]

@router.get("/global", response_model=List[MentalHealthData], summary="Obtener datos de salud mental global")
def get_global_mental_health_data():
    """
    Simula la obtención de los datos de salud mental global más recientes.
    """
    return SIMULATED_DATA

@router.get("/historical", response_model=List[MentalHealthData], summary="Obtener datos históricos de salud mental")
def get_historical_mental_health_data(region: str = "Europe", start_date: date = date(2020, 1, 1), end_date: date = date(2025, 1, 1)):
    """
    Simula la obtención de datos históricos de salud mental para una región específica.
    """
    # En una implementación real, esto consultaría la base de datos
    return [
        {
            "region": region,
            "date": start_date,
            "psychiatric_admissions": 1000,
            "suicide_rate": 10.0,
            "bipolar_episodes": 50,
            "depression_index": 60.0
        },
        {
            "region": region,
            "date": end_date,
            "psychiatric_admissions": 1200,
            "suicide_rate": 12.0,
            "bipolar_episodes": 70,
            "depression_index": 65.0
        }
    ]
