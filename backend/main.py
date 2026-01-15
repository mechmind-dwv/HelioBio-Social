# backend/main.py
# Punto de entrada principal para la aplicación FastAPI

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from backend.config import settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulación de eventos de inicio/apagado
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de inicio
    logger.info("Aplicación HelioBio-Social iniciándose...")
    # Aquí se inicializarían la conexión a la DB, Redis, etc.
    # from backend.database.database import init_db
    # init_db()
    yield
    # Evento de apagado
    logger.info("Aplicación HelioBio-Social apagándose...")

app = FastAPI(
    title="HelioBio-Social API",
    version="3.0.0",
    description="API para correlacionar actividad solar con salud mental global.",
    lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost:3000",  # Frontend
    "http://localhost:8000",  # Backend
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
    return {"message": "Bienvenido a la API de HelioBio-Social", "version": app.version}

@app.get("/status")
def get_status():
    # Aquí se verificaría el estado de la DB, Redis, etc.
    return {"status": "ok", "environment": settings.ENVIRONMENT, "db_connection": "simulated_ok", "redis_connection": "simulated_ok"}

# Incluir routers de API
from backend.api.v1 import solar, mental_health
app.include_router(solar.router, prefix="/api/v1/solar", tags=["solar"])
app.include_router(mental_health.router, prefix="/api/v1/mental", tags=["mental_health"])

# Si se ejecuta como script (para CLI commands)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run-analysis":
        logger.info(f"Ejecutando análisis con parámetros: {sys.argv[2:]}")
        # Lógica de CLI aquí
    elif len(sys.argv) > 1 and sys.argv[1] == "generate-report":
        logger.info(f"Generando reporte con parámetros: {sys.argv[2:]}")
        # Lógica de CLI aquí
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
