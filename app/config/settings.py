"""
⚙️ Configuración del Sistema HelioBio-Social - Compatible con Pydantic v2
"""
import os
from typing import Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuración principal del sistema - Compatible Pydantic v2"""
    
    # Configuración de la aplicación
    app_name: str = "HelioBio-Social v1.3.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Facebook API Configuration (opcional por ahora)
    facebook_app_id: str = Field(default="", env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(default="", env="FACEBOOK_APP_SECRET")
    facebook_access_token: str = Field(default="", env="FACEBOOK_ACCESS_TOKEN")
    facebook_page_id: str = Field(default="", env="FACEBOOK_PAGE_ID")
    
    # Google Cloud Configuration (opcional por ahora)
    google_cloud_project: str = Field(default="", env="GOOGLE_CLOUD_PROJECT")
    google_application_credentials: str = Field(default="", env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Solar Data Sources
    noaa_api_base: str = Field(default="https://services.swpc.noaa.gov/json/", env="NOAA_API_BASE")
    nasa_api_key: str = Field(default="demo_key", env="NASA_API_KEY")
    silso_data_url: str = Field(default="http://www.sidc.be/silso/DATA/SN_d_tot_V2.0.csv", env="SILSO_DATA_URL")
    
    # Analysis Parameters
    correlation_methods: List[str] = ["pearson", "spearman", "granger", "wavelet"]
    time_windows: Dict[str, int] = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "11_year_cycle": 4018
    }
    confidence_threshold: float = 0.05
    
    # Chizhevsky Parameters
    solar_max_amplification: float = 1.8
    geomagnetic_sensitivity: float = 0.7
    social_crispation_threshold: float = 0.65
    
    # Alert System Parameters
    alert_retention_days: int = Field(default=7, env="ALERT_RETENTION_DAYS")
    max_active_alerts: int = 10
    
    # Data Management
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar variables extra

# Instancia global de configuración
_settings_instance = None

def get_settings() -> Settings:
    """Obtener instancia de configuración (singleton)"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

def get_chizhevsky_parameters() -> Dict[str, Any]:
    """Obtener parámetros específicos del modelo Chizhevsky"""
    settings = get_settings()
    return {
        "solar_max_amplification": settings.solar_max_amplification,
        "geomagnetic_sensitivity": settings.geomagnetic_sensitivity,
        "social_crispation_threshold": settings.social_crispation_threshold,
        "time_windows": settings.time_windows
    }
