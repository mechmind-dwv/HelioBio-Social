"""
🔔 SISTEMA DE ALERTAS INTELIGENTES HELIOBIO-SOCIAL
Sistema avanzado de detección y notificación de eventos críticos
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING" 
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    SOLAR = "SOLAR"
    SOCIAL = "SOCIAL"
    CORRELATION = "CORRELATION"
    SYSTEM = "SYSTEM"

@dataclass
class Alert:
    id: int
    level: AlertLevel
    type: AlertType
    title: str
    message: str
    timestamp: datetime
    duration_hours: int
    acknowledged: bool = False
    data: Optional[Dict[str, Any]] = None

class AlertSystem:
    """
    Sistema avanzado de alertas para monitoreo heliobio-social
    """
    
    def __init__(self):
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.next_alert_id = 0
        self.status = "initializing"
        
        # Umbrales para alertas
        self.thresholds = {
            "solar_flare_high": 4,  # Nivel de fulgraciones
            "geomagnetic_storm": 3,  # Nivel de tormenta geomagnética
            "social_conflict_high": 0.8,  # Métrica de conflicto
            "engagement_spike": 0.3,  # Cambio brusco en engagement
            "resonance_critical": 0.8,  # Resonancia crítica
        }
        
        logger.info("🔔 Sistema de alertas inteligentes inicializado")
    
    async def start_alert_monitoring(self):
        """Iniciar monitoreo continuo de alertas"""
        self.status = "monitoring"
        logger.info("🚨 Iniciando monitoreo de alertas en tiempo real...")
        
        # Monitoreo en background
        asyncio.create_task(self._continuous_alert_check())
    
    async def _continuous_alert_check(self):
        """Verificación continua de condiciones para alertas"""
        while self.status == "monitoring":
            try:
                # Aquí se integraría con los otros componentes del sistema
                # Para este ejemplo, generamos alertas simuladas
                await self._check_simulated_alerts()
                await asyncio.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error en monitoreo de alertas: {e}")
                await asyncio.sleep(30)
    
    async def _check_simulated_alerts(self):
        """Generar alertas simuladas para demostración"""
        from app.core.solar_monitor import SolarMonitor
        from app.core.social_analyzer import SocialAnalyzer
        
        # Alertas solares simuladas
        if len(self.active_alerts) < 2:  # Limitar número de alertas activas
            solar_alert = self._create_solar_alert()
            if solar_alert:
                self.add_alert(solar_alert)
            
            social_alert = self._create_social_alert() 
            if social_alert:
                self.add_alert(social_alert)
    
    def _create_solar_alert(self):
        """Crear alerta solar de ejemplo"""
        if len([a for a in self.active_alerts if a.type == AlertType.SOLAR]) == 0:
            return Alert(
                id=self._get_next_alert_id(),
                level=AlertLevel.WARNING,
                type=AlertType.SOLAR,
                title="🧲 TORMENTA GEOMAGNÉTICA ACTIVA",
                message="Tormenta geomagnética nivel 3/4. Afectación potencial en sistemas biológicos y estados de ánimo.",
                timestamp=datetime.utcnow(),
                duration_hours=6,
                data={"storm_level": 3, "impact": "medium"}
            )
        return None
    
    def _create_social_alert(self):
        """Crear alerta social de ejemplo"""
        if len([a for a in self.active_alerts if a.type == AlertType.SOCIAL]) == 0:
            return Alert(
                id=self._get_next_alert_id(),
                level=AlertLevel.INFO,
                type=AlertType.SOCIAL,
                title="📊 ANOMALÍA EN PARTICIPACIÓN SOCIAL",
                message="Aumento brusco del engagement (+38.3%). Posible evento viral o cambio de tendencia.",
                timestamp=datetime.utcnow(),
                duration_hours=2,
                data={"engagement_change": 0.383, "current_engagement": 70.62}
            )
        return None
    
    def add_alert(self, alert: Alert):
        """Añadir una nueva alerta al sistema"""
        # Verificar si ya existe una alerta similar
        similar_alerts = [
            a for a in self.active_alerts 
            if a.type == alert.type and a.title == alert.title
        ]
        
        if not similar_alerts:
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
            logger.info(f"🚨 Nueva alerta: {alert.title} (Nivel: {alert.level.value})")
            
            # Notificación (en un sistema real, aquí irían webhooks, emails, etc.)
            self._notify_alert(alert)
    
    def _notify_alert(self, alert: Alert):
        """Notificar alerta (placeholder para integraciones futuras)"""
        # Aquí se integraría con:
        # - Webhooks para aplicaciones externas
        # - Sistema de email/SMS
        # - Notificaciones push
        # - Integración con Slack/Discord/etc.
        
        notification_msg = f"""
        🔔 ALERTA HELIOBIO-SOCIAL 🔔
        
        Nivel: {alert.level.value}
        Tipo: {alert.type.value}
        Título: {alert.title}
        Mensaje: {alert.message}
        Timestamp: {alert.timestamp}
        
        Acción requerida: {self._get_required_action(alert)}
        """
        
        logger.info(f"📢 Notificación de alerta:\n{notification_msg}")
    
    def _get_required_action(self, alert: Alert) -> str:
        """Obtener acción requerida basada en el tipo de alerta"""
        actions = {
            AlertType.SOLAR: "Monitorear actividad solar y posibles efectos en sistemas biológicos",
            AlertType.SOCIAL: "Analizar tendencias sociales y preparar respuestas estratégicas", 
            AlertType.CORRELATION: "Evaluar impacto en resonancia solar-social y predicciones",
            AlertType.SYSTEM: "Revisar estado del sistema y componentes afectados"
        }
        return actions.get(alert.type, "Monitorizar situación")
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Reconocer una alerta activa"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"✅ Alerta {alert_id} reconocida: {alert.title}")
                return True
        return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtener alertas activas en formato serializable"""
        now = datetime.utcnow()
        
        # Limpiar alertas expiradas
        self.active_alerts = [
            alert for alert in self.active_alerts
            if now - alert.timestamp < timedelta(hours=alert.duration_hours)
        ]
        
        return [
            {
                "id": alert.id,
                "level": alert.level.value,
                "type": alert.type.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "duration_hours": alert.duration_hours,
                "acknowledged": alert.acknowledged,
                "data": alert.data or {}
            }
            for alert in self.active_alerts
        ]
    
    def get_24h_stats(self) -> int:
        """Obtener estadísticas de alertas en las últimas 24 horas"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        return len([
            alert for alert in self.alert_history
            if alert.timestamp > cutoff
        ])
    
    def _get_next_alert_id(self) -> int:
        """Obtener siguiente ID de alerta"""
        self.next_alert_id += 1
        return self.next_alert_id
    
    async def stop_monitoring(self):
        """Detener monitoreo de alertas"""
        self.status = "stopped"
        logger.info("🛑 Monitoreo de alertas detenido")
