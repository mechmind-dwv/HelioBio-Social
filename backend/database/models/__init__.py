# backend/database/models/__init__.py
from .mental_health_data import MentalHealthData, MentalHealthSummary
# Importar otros modelos aquí a medida que se creen, por ejemplo:
# from .solar_data import SolarData

__all__ = [
    "MentalHealthData",
    "MentalHealthSummary",
    # "SolarData",
]
