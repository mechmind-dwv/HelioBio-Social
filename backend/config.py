# backend/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración general
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8222
    
    # Configuración de la base de datos
    POSTGRES_USER: str = "heliobio_user"
    POSTGRES_PASSWORD: str = "heliobio_password"
    POSTGRES_DB: str = "heliobio_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Configuración de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Claves API
    NASA_API_KEY: str = "DEMO_KEY"
    OPENAI_API_KEY: str = ""
    
    # Configuración del modelo - IMPORTANTE: extra='ignore'
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',  # Esto permite campos extra sin error
        case_sensitive=True
    )

settings = Settings()

def get_db_url():
    return f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def get_redis_url():
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
