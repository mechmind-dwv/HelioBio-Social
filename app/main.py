"""
🌞 HELIOBIO-SOCIAL v1.3.0 - SISTEMA CORREGIDO
Versión compatible con Pydantic v2 y sin dependencias problemáticas
"""
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import random
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("helio_bio_social")

# Datos globales del sistema
historical_data = []
active_alerts = []
next_alert_id = 0

class AlertSystem:
    """Sistema de alertas simplificado"""
    
    def __init__(self):
        self.active_alerts = []
        self.alert_history = []
    
    async def analyze_conditions(self, solar_data, social_data, resonance):
        """Analizar condiciones para generar alertas"""
        new_alerts = []
        
        # Alerta por alta actividad solar
        if solar_data.get('sunspot_number', 0) > 80:
            new_alerts.append({
                'level': 'WARNING',
                'type': 'SOLAR',
                'title': '🌞 ALTA ACTIVIDAD SOLAR',
                'message': f"Manchas solares en {solar_data['sunspot_number']}. Influencia elevada en psique colectiva.",
                'timestamp': datetime.utcnow(),
                'duration_hours': 6
            })
        
        # Alerta por alta resonancia
        if resonance > 0.7:
            new_alerts.append({
                'level': 'CRITICAL', 
                'type': 'CORRELATION',
                'title': '🔗 RESONANCIA CRÍTICA',
                'message': f"Resonancia solar-social en {resonance:.1%}. Condiciones para eventos sociales significativos.",
                'timestamp': datetime.utcnow(),
                'duration_hours': 12
            })
        
        # Alerta por conflicto social elevado
        if social_data.get('conflict_metric', 0) > 0.7:
            new_alerts.append({
                'level': 'WARNING',
                'type': 'SOCIAL', 
                'title': '👥 TENSIÓN SOCIAL ELEVADA',
                'message': f"Conflicto social en {social_data['conflict_metric']:.1%}. Crispación detectable.",
                'timestamp': datetime.utcnow(),
                'duration_hours': 4
            })
        
        return new_alerts
    
    async def get_active_alerts(self):
        """Obtener alertas activas"""
        now = datetime.utcnow()
        # Filtrar alertas expiradas
        self.active_alerts = [
            alert for alert in self.active_alerts
            if now - alert['timestamp'] < timedelta(hours=alert['duration_hours'])
        ]
        return self.active_alerts
    
    async def get_alert_stats(self):
        """Obtener estadísticas de alertas"""
        now = datetime.utcnow()
        alerts_24h = len([
            alert for alert in self.alert_history
            if now - alert['timestamp'] < timedelta(hours=24)
        ])
        
        return {
            "active_alerts": len(self.active_alerts),
            "alerts_24h": alerts_24h,
            "critical_alerts": len([a for a in self.active_alerts if a['level'] == 'CRITICAL']),
            "warning_alerts": len([a for a in self.active_alerts if a['level'] == 'WARNING']),
            "solar_alerts": len([a for a in self.active_alerts if a['type'] == 'SOLAR']),
            "social_alerts": len([a for a in self.active_alerts if a['type'] == 'SOCIAL'])
        }
    
    async def acknowledge_alert(self, alert_id: int):
        """Reconocer alerta (simulado)"""
        logger.info(f"Alerta {alert_id} reconocida")

class SolarService:
    """Servicio solar simplificado"""
    
    async def get_current_solar_data(self):
        """Obtener datos solares simulados"""
        return {
            'sunspot_number': random.randint(20, 120),
            'solar_flux': random.uniform(70, 130),
            'flare_activity': random.randint(0, 5),
            'geomagnetic_storm': random.randint(0, 4),
            'solar_wind_speed': random.randint(300, 600),
            'coronal_holes': random.randint(0, 3),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'enhanced_simulation',
            'solar_cycle_phase': 'late_ascending',
            'cycle_progress': 0.45
        }

class SocialAnalyzerService:
    """Servicio de análisis social simplificado"""
    
    async def get_social_analysis(self):
        """Obtener análisis social simulado"""
        topics = [
            {"name": "Crisis Económicas", "sentiment": random.uniform(-0.7, -0.3), "engagement": random.uniform(70, 90)},
            {"name": "Política Internacional", "sentiment": random.uniform(-0.6, -0.2), "engagement": random.uniform(65, 85)},
            {"name": "Cambio Climático", "sentiment": random.uniform(-0.3, 0.1), "engagement": random.uniform(60, 80)},
            {"name": "Salud Pública", "sentiment": random.uniform(-0.2, 0.2), "engagement": random.uniform(55, 75)},
            {"name": "Tecnología IA", "sentiment": random.uniform(0.1, 0.5), "engagement": random.uniform(50, 70)}
        ]
        
        return {
            'engagement_intensity': random.uniform(50, 90),
            'sentiment_polarity': random.uniform(-0.5, 0.5),
            'sentiment_subjectivity': random.uniform(0.2, 0.4),
            'conflict_metric': random.uniform(0.1, 0.9),
            'viral_content': random.randint(3, 10),
            'active_users': random.randint(800000, 1500000),
            'trending_topics': topics,
            'dominant_emotion': random.choice(['neutral', 'positive', 'negative']),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'enhanced_social_analysis'
        }

# Inicializar servicios
solar_service = SolarService()
social_service = SocialAnalyzerService()
alert_system = AlertSystem()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del sistema"""
    global historical_data
    
    print("🎆 HELIOBIO-SOCIAL v1.3.0 - SISTEMA INICIADO")
    print("🚨 Sistema de alertas inteligentes activado")
    
    try:
        # Inicializar con datos
        await update_system_data()
        # Iniciar actualización continua
        asyncio.create_task(continuous_data_update())
        
        print("✅ Sistema funcionando correctamente")
        yield
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        raise
    finally:
        print("🛑 Apagando sistema...")

async def update_system_data():
    """Actualizar datos del sistema"""
    global historical_data
    
    solar_data = await solar_service.get_current_solar_data()
    social_data = await social_service.get_social_analysis()
    resonance = calculate_resonance(solar_data, social_data)
    
    # Generar alertas
    new_alerts = await alert_system.analyze_conditions(solar_data, social_data, resonance)
    for alert in new_alerts:
        if alert not in alert_system.active_alerts:
            alert_system.active_alerts.append(alert)
            alert_system.alert_history.append(alert)
    
    # Guardar histórico
    historical_point = {
        'timestamp': datetime.utcnow().isoformat(),
        'solar': solar_data,
        'social': social_data,
        'resonance': resonance,
        'alerts_triggered': len(new_alerts)
    }
    
    historical_data.append(historical_point)
    if len(historical_data) > 100:
        historical_data.pop(0)

async def continuous_data_update():
    """Actualización continua cada 30 segundos"""
    while True:
        await update_system_data()
        await asyncio.sleep(30)

def calculate_resonance(solar, social):
    """Calcular resonancia solar-social"""
    solar_intensity = solar.get('sunspot_number', 0) / 150.0
    social_tension = social.get('conflict_metric', 0)
    flare_impact = solar.get('flare_activity', 0) / 5.0
    
    resonance = (solar_intensity * 0.4 + social_tension * 0.4 + flare_impact * 0.2)
    return min(1.0, resonance)

# CREAR APLICACIÓN FASTAPI
app = FastAPI(
    title="HelioBio-Social API",
    description="Sistema de Análisis Heliobiológico con Alertas Inteligentes",
    version="1.3.0",
    lifespan=lifespan
)

# Configuración de middleware y archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENDPOINTS PRINCIPALES
@app.get("/")
async def serve_dashboard():
    """Servir dashboard principal"""
    return FileResponse('app/static/dashboard.html')

@app.get("/api/health")
async def health_check():
    """Estado del sistema"""
    alert_stats = await alert_system.get_alert_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "alerts-1.3",
        "components": {
            "solar_monitor": "enhanced_simulation",
            "social_analyzer": "enhanced_social_analysis", 
            "alert_system": "active",
            "dashboard": "active"
        },
        "alert_stats": alert_stats
    }

@app.get("/api/solar/current")
async def get_current_solar_activity():
    """Actividad solar actual"""
    solar_data = historical_data[-1]['solar'] if historical_data else await solar_service.get_current_solar_data()
    
    return {
        "solar_activity": solar_data,
        "chizhevsky_interpretation": get_solar_interpretation(solar_data),
        "data_source": "enhanced_simulation"
    }

@app.get("/api/social/analysis")
async def get_social_analysis():
    """Análisis social actual"""
    social_data = historical_data[-1]['social'] if historical_data else await social_service.get_social_analysis()
    
    return {
        "social_analysis": social_data,
        "collective_mood": get_social_mood(social_data),
        "data_source": "enhanced_social_analysis"
    }

@app.get("/api/social/trending")
async def get_trending_topics():
    """Temas trending"""
    social_data = historical_data[-1]['social'] if historical_data else await social_service.get_social_analysis()
    
    return {
        "trending_topics": social_data.get('trending_topics', []),
        "dominant_emotion": social_data.get('dominant_emotion', 'neutral'),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/correlation/realtime")
async def get_realtime_correlation():
    """Correlación en tiempo real"""
    if not historical_data:
        raise HTTPException(status_code=503, detail="Sistema inicializando...")
    
    resonance = historical_data[-1]['resonance']
    solar_data = historical_data[-1]['solar']
    
    interpretation = "ALTA RESONANCIA" if resonance > 0.7 else "RESONANCIA MODERADA" if resonance > 0.4 else "RESONANCIA BAJA"
    
    return {
        "correlation_analysis": {
            "solar_social_resonance": round(resonance, 3),
            "interpretation": interpretation,
            "confidence": 0.85,
            "solar_cycle_phase": solar_data.get('solar_cycle_phase', 'unknown')
        },
        "crispation_alert": {
            "level": "HIGH" if resonance > 0.7 else "MODERATE" if resonance > 0.5 else "LOW",
            "message": get_alert_message(resonance)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Alertas activas"""
    active_alerts = await alert_system.get_active_alerts()
    
    return {
        "alerts": [
            {
                "id": idx,
                "level": alert["level"],
                "type": alert["type"],
                "title": alert["title"],
                "message": alert["message"],
                "timestamp": alert["timestamp"].isoformat(),
                "duration_hours": alert["duration_hours"],
                "data": {}
            }
            for idx, alert in enumerate(active_alerts)
        ],
        "total_active": len(active_alerts),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/alerts/stats")
async def get_alert_stats():
    """Estadísticas de alertas"""
    return await alert_system.get_alert_stats()

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """Reconocer alerta"""
    await alert_system.acknowledge_alert(alert_id)
    return {"status": "acknowledged", "alert_id": alert_id}

@app.get("/api/historical/data")
async def get_historical_data(hours: int = 6):
    """Datos históricos"""
    if not historical_data:
        return {"time_range_hours": hours, "data_points": 0, "data": []}
    
    cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
    filtered_data = [
        point for point in historical_data 
        if datetime.fromisoformat(point['timestamp']).timestamp() > cutoff_time
    ]
    
    return {
        "time_range_hours": hours,
        "data_points": len(filtered_data),
        "data": filtered_data[-50:]  # Últimos 50 puntos
    }

# Funciones auxiliares
def get_solar_interpretation(solar_data):
    sunspots = solar_data.get('sunspot_number', 0)
    if sunspots > 100:
        return "🌋 ACTIVIDAD SOLAR ELEVADA - Máxima influencia en psique colectiva"
    elif sunspots > 60:
        return "🔥 ACTIVIDAD MODERADA-ALTA - Influencia significativa detectada"
    elif sunspots > 30:
        return "⚡ ACTIVIDAD MODERADA - Influencia en tono emocional"
    else:
        return "🌊 ACTIVIDAD BAJA - Influencia solar mínima"

def get_social_mood(social_data):
    emotion = social_data.get('dominant_emotion', 'neutral')
    conflict = social_data.get('conflict_metric', 0)
    
    if conflict > 0.7:
        return "🔥 ALTA POLARIZACIÓN - Condiciones de conflicto"
    elif emotion == 'positive' and conflict < 0.3:
        return "🌟 ARMONÍA COLECTIVA - Estados positivos dominantes"
    elif emotion == 'negative':
        return "🌪️ TENSIÓN DETECTABLE - Estados negativos"
    else:
        return "🌊 ESTADO NEUTRO - Condiciones base estables"

def get_alert_message(resonance):
    if resonance > 0.7:
        return "🚨 ALTA RESONANCIA - Eventos sociales significativos probables"
    elif resonance > 0.5:
        return "📡 RESONANCIA MODERADA - Monitorizar tendencias"
    else:
        return "✅ CONDICIONES ESTABLES - Resonancia normal"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
