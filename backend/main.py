# backend/main.py
# Punto de entrada principal para la aplicación FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import Base, engine
from api.v1 import mental_health

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Eventos de inicio/apagado
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicación HelioBio-Social iniciándose...")
    # Aquí se inicializarían conexiones a DB, Redis, etc.
    yield
    logger.info("Aplicación HelioBio-Social apagándose...")

app = FastAPI(
    title="HelioBio-Social API",
    version="3.0.0",
    description="API para correlacionar actividad solar con salud mental global.",
    lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8222",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de prueba
@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a la API de HelioBio-Social",
        "version": app.version
    }

@app.get("/status")
def get_status():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database": "SQLite connected"
    }

@app.include_router(
    mental_health.router,
    prefix="/api/v1/mental-health",
    tags=["mental_health"]
)
# Incluir routers cuando estén listos
# from api.v1 import solar, mental_health
# app.include_router(solar.router, prefix="/api/v1/solar", tags=["solar"])
# app.include_router(mental_health.router, prefix="/api/v1/mental", tags=["mental_health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8222)
