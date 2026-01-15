from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./heliobio.db"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "HelioBio-Social"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_db_url_sqlite():
    return "sqlite:///./heliobio.db"
