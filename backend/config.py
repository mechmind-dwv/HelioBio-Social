# backend/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración general
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    
    # Configuración de la base de datos
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    
    # Configuración de Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Claves API
    NASA_API_KEY: str = "DEMO_KEY"
    OPENAI_API_KEY: str = ""
    
    # Configuración del modelo de pydantic-settings
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()

def get_db_url():
    # Usamos asyncpg para FastAPI, pero la URL de SQLAlchemy es útil para Alembic
    return f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def get_redis_url():
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

if __name__ == "__main__":
    print("Configuración cargada:")
    print(f"Entorno: {settings.ENVIRONMENT}")
    print(f"DB URL (ejemplo): {get_db_url()}")
    print(f"Redis URL: {get_redis_url()}")
