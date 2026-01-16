"""
Main FastAPI application with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Dict, List
import logging
from datetime import datetime

from connectors import noaa_connector, who_connector, trends_connector
from analytics.correlation_engine import correlation_engine
from alerts.alert_engine import alert_engine
from alerts.notifications import notification_service

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestor de conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los clientes conectados"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Eliminar conexiones desconectadas
        for connection in disconnected:
            self.disconnect(connection)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Inicialización
    logger.info("🚀 Starting HelioBio-Social v3.0")
    
    # Conectar a APIs
    logger.info("Connecting to external APIs...")
    
    # Iniciar tareas en segundo plano
    app.state.monitoring_task = asyncio.create_task(monitoring_loop(app))
    
    yield
    
    # Limpieza
    logger.info("Shutting down HelioBio-Social...")
    app.state.monitoring_task.cancel()
    
    # Cerrar conexiones
    await noaa_connector.close()
    await who_connector.close()

# Crear aplicación FastAPI
app = FastAPI(
    title="HelioBio-Social API",
    description="Scientific API for Solar-Mental Health Correlation Analysis",
    version="3.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://heliobio.social"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manager para WebSocket
manager = ConnectionManager()

# Tarea de monitoreo en segundo plano
async def monitoring_loop(app: FastAPI):
    """
    Loop principal de monitoreo y análisis
    """
    logger.info("Starting monitoring loop...")
    
    while True:
        try:
            # 1. Obtener datos solares
            solar_data = await noaa_connector.fetch_realtime_data()
            solar_dict = {
                "timestamp": solar_data.timestamp.isoformat(),
                "kp_index": solar_data.kp_index,
                "solar_wind_speed": solar_data.solar_wind_speed,
                "bz": solar_data.bz,
                "solar_wind_density": solar_data.solar_wind_density
            }
            
            # Broadcast datos solares
            await manager.broadcast({
                "type": "solar_update",
                "payload": solar_dict
            })
            
            # 2. Verificar tormentas geomagnéticas
            storm_check = await noaa_connector.check_geomagnetic_storm()
            if storm_check.get("storm_active"):
                # Generar alerta
                alerts = await alert_engine.evaluate_solar_data(storm_check)
                for alert in alerts:
                    alert_dict = alert.to_dict()
                    await manager.broadcast({
                        "type": "alert",
                        "payload": alert_dict
                    })
            
            # 3. Obtener datos de salud mental (cada 6 horas)
            # En producción, esto sería más complejo con caching
            
            # 4. Calcular correlaciones (cada hora)
            # En producción, usar datos históricos
            
            # 5. Enviar métricas del sistema
            metrics = {
                "active_alerts": len(alert_engine.active_alerts),
                "data_points": 0,  # Actualizar con conteo real
                "correlation_strength": 0,  # Actualizar con cálculo real
                "prediction_accuracy": 0,  # Actualizar con cálculo real
                "last_update": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast({
                "type": "metrics_update",
                "payload": metrics
            })
            
            # Esperar antes de siguiente iteración
            await asyncio.sleep(60)  # 1 minuto
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(10)

# Endpoints WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexión activa
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Endpoints REST
@app.get("/")
async def root():
    return {
        "message": "🌞 HelioBio-Social API v3.0",
        "description": "Scientific analysis of solar-mental health correlations",
        "version": "3.0.0",
        "docs": "/docs",
        "websocket": "/ws",
        "endpoints": {
            "solar": "/api/v1/solar",
            "mental-health": "/api/v1/mental-health",
            "correlation": "/api/v1/correlation",
            "alerts": "/api/v1/alerts"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "noaa_api": "connected",
            "who_api": "connected",
            "analytics": "active",
            "alerts": "active"
        }
    }

# Incluir routers específicos
from api.v1 import solar, mental_health, correlation, alerts

app.include_router(solar.router, prefix="/api/v1/solar", tags=["Solar Data"])
app.include_router(mental_health.router, prefix="/api/v1/mental-health", tags=["Mental Health"])
app.include_router(correlation.router, prefix="/api/v1/correlation", tags=["Correlation Analysis"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alert System"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
