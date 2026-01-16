"""
Sistema de alertas inteligente para HelioBio-Social
Monitoriza correlaciones y genera alertas cuando se detectan patrones significativos
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Niveles de severidad de alerta"""
    INFO = "INFO"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    """Tipos de alerta"""
    CORRELATION_SPIKE = "CORRELATION_SPIKE"
    GEOMAGNETIC_STORM = "GEOMAGNETIC_STORM"
    MENTAL_HEALTH_SPIKE = "MENTAL_HEALTH_SPIKE"
    PREDICTION_ALERT = "PREDICTION_ALERT"
    SYSTEM_ALERT = "SYSTEM_ALERT"

@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir alerta a diccionario"""
        return {
            'id': self.id,
            'type': self.type.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class AlertRule:
    """Regla para generar alertas"""
    
    def __init__(self, name: str, condition: Callable[[Dict[str, Any]], bool],
                 alert_type: AlertType, severity: AlertSeverity,
                 message_template: str, cooldown_minutes: int = 60):
        """
        Args:
            name: Nombre de la regla
            condition: Función que evalúa si se debe generar alerta
            alert_type: Tipo de alerta
            severity: Severidad
            message_template: Plantilla para mensaje
            cooldown_minutes: Tiempo mínimo entre alertas del mismo tipo
        """
        self.name = name
        self.condition = condition
        self.alert_type = alert_type
        self.severity = severity
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
    
    def should_trigger(self, data: Dict[str, Any]) -> bool:
        """Determinar si la regla debe disparar una alerta"""
        # Verificar cooldown
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False
        
        # Evaluar condición
        try:
            return self.condition(data)
        except Exception as e:
            logger.error(f"Error evaluating alert rule {self.name}: {e}")
            return False
    
    def create_alert(self, data: Dict[str, Any]) -> Alert:
        """Crear alerta a partir de datos"""
        # Formatear mensaje
        message = self.message_template.format(**data)
        
        # Crear ID único
        alert_id = f"{self.alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(data)) % 10000:04d}"
        
        # Determinar expiración
        expires_at = None
        if self.severity == AlertSeverity.CRITICAL:
            expires_at = datetime.now() + timedelta(hours=1)
        elif self.severity == AlertSeverity.HIGH:
            expires_at = datetime.now() + timedelta(hours=6)
        elif self.severity == AlertSeverity.MODERATE:
            expires_at = datetime.now() + timedelta(days=1)
        
        alert = Alert(
            id=alert_id,
            type=self.alert_type,
            severity=self.severity,
            title=f"Alerta {self.severity.value}: {self.alert_type.value}",
            message=message,
            timestamp=datetime.now(),
            data=data,
            expires_at=expires_at
        )
        
        # Actualizar último disparo
        self.last_triggered = datetime.now()
        
        return alert

class AlertEngine:
    """Motor principal de alertas"""
    
    def __init__(self, notification_channels: List[str] = None):
        """Inicializar motor de alertas"""
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_channels = notification_channels or ['log']
        
        # Registrar reglas por defecto
        self._register_default_rules()
        
        logger.info("AlertEngine initialized with %d rules", len(self.rules))
    
    def _register_default_rules(self):
        """Registrar reglas de alerta por defecto"""
        
        # 1. Regla para tormentas geomagnéticas fuertes
        def strong_geomagnetic_storm(data: Dict[str, Any]) -> bool:
            kp = data.get('kp_index', 0)
            storm_level = data.get('storm_level', 'NONE')
            return kp >= 6 or storm_level in ['STRONG', 'SEVERE']
        
        self.register_rule(AlertRule(
            name="strong_geomagnetic_storm",
            condition=strong_geomagnetic_storm,
            alert_type=AlertType.GEOMAGNETIC_STORM,
            severity=AlertSeverity.HIGH,
            message_template="Tormenta geomagnética fuerte detectada: Kp={kp_index}, Nivel={storm_level}. "
                           "Esperar posibles efectos en salud mental en 3-5 días.",
            cooldown_minutes=360  # 6 horas
        ))
        
        # 2. Regla para pico de correlación
        def correlation_spike(data: Dict[str, Any]) -> bool:
            correlation = data.get('correlation', 0)
            p_value = data.get('p_value', 1)
            window_size = data.get('window_size', 30)
            
            # Correlación fuerte y significativa en ventana reciente
            return (abs(correlation) > 0.6 and 
                    p_value < 0.01 and 
                    window_size >= 7)
        
        self.register_rule(AlertRule(
            name="correlation_spike",
            condition=correlation_spike,
            alert_type=AlertType.CORRELATION_SPIKE,
            severity=AlertSeverity.MODERATE,
            message_template="Pico de correlación detectado: r={correlation:.3f}, p={p_value:.4f}. "
                           "Actividad solar correlacionada fuertemente con indicadores de salud mental.",
            cooldown_minutes=120
        ))
        
        # 3. Regla para aumento en indicadores de salud mental
        def mental_health_spike(data: Dict[str, Any]) -> bool:
            increase_percent = data.get('increase_percent', 0)
            baseline = data.get('baseline', 0)
            current = data.get('current', 0)
            
            # Aumento del 25% o más sobre la línea base
            return (increase_percent >= 25 and 
                    current > baseline and 
                    baseline > 0)
        
        self.register_rule(AlertRule(
            name="mental_health_spike",
            condition=mental_health_spike,
            alert_type=AlertType.MENTAL_HEALTH_SPIKE,
            severity=AlertSeverity.HIGH,
            message_template="Aumento significativo en indicadores de salud mental: "
                           "+{increase_percent:.0f}% sobre línea base. "
                           "Valor actual: {current:.1f}, Línea base: {baseline:.1f}.",
            cooldown_minutes=180
        ))
        
        # 4. Regla para predicción de riesgo alto
        def high_risk_prediction(data: Dict[str, Any]) -> bool:
            risk_score = data.get('risk_score', 0)
            confidence = data.get('confidence', 0)
            
            return risk_score >= 0.7 and confidence >= 0.8
        
        self.register_rule(AlertRule(
            name="high_risk_prediction",
            condition=high_risk_prediction,
            alert_type=AlertType.PREDICTION_ALERT,
            severity=AlertSeverity.CRITICAL,
            message_template="Predicción de alto riesgo: score={risk_score:.2f}, "
                           "confianza={confidence:.2f}. "
                           "Se esperan aumentos significativos en indicadores críticos.",
            cooldown_minutes=240
        ))
    
    def register_rule(self, rule: AlertRule):
        """Registrar una nueva regla de alerta"""
        self.rules.append(rule)
        logger.info(f"Registered alert rule: {rule.name}")
    
    async def evaluate_data(self, data_source: str, data: Dict[str, Any]) -> List[Alert]:
        """Evaluar datos contra todas las reglas registradas"""
        triggered_alerts = []
        
        for rule in self.rules:
            try:
                if rule.should_trigger(data):
                    alert = rule.create_alert(data)
                    
                    # Agregar metadata adicional
                    alert.data['data_source'] = data_source
                    alert.data['rule_name'] = rule.name
                    
                    # Guardar alerta
                    self.active_alerts[alert.id] = alert
                    self.alert_history.append(alert)
                    
                    triggered_alerts.append(alert)
                    
                    # Enviar notificaciones
                    await self._send_notifications(alert)
                    
                    logger.info(f"Alert triggered: {alert.id} - {alert.title}")
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                continue
        
        # Limpiar alertas expiradas
        self._clean_expired_alerts()
        
        return triggered_alerts
    
    async def evaluate_solar_data(self, solar_data: Dict[str, Any]) -> List[Alert]:
        """Evaluación especializada para datos solares"""
        alerts = await self.evaluate_data('solar', solar_data)
        return alerts
    
    async def evaluate_correlation_data(self, correlation_data: Dict[str, Any]) -> List[Alert]:
        """Evaluación especializada para datos de correlación"""
        alerts = await self.evaluate_data('correlation', correlation_data)
        return alerts
    
    async def evaluate_mental_health_data(self, mental_health_data: Dict[str, Any]) -> List[Alert]:
        """Evaluación especializada para datos de salud mental"""
        alerts = await self.evaluate_data('mental_health', mental_health_data)
        return alerts
    
    async def _send_notifications(self, alert: Alert):
        """Enviar notificaciones por canales configurados"""
        
        for channel in self.notification_channels:
            try:
                if channel == 'log':
                    self._send_log_notification(alert)
                elif channel == 'email':
                    await self._send_email_notification(alert)
                elif channel == 'webhook':
                    await self._send_webhook_notification(alert)
                elif channel == 'slack':
                    await self._send_slack_notification(alert)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
    
    def _send_log_notification(self, alert: Alert):
        """Enviar notificación a log"""
        log_message = f"""
        🚨 ALERTA {alert.severity.value} - {alert.type.value}
        Título: {alert.title}
        Mensaje: {alert.message}
        Timestamp: {alert.timestamp}
        Datos: {json.dumps(alert.data, indent=2, default=str)}
        """
        logger.warning(log_message)
    
    async def _send_email_notification(self, alert: Alert):
        """Enviar notificación por email"""
        # Configuración de email (debería venir de variables de entorno)
        smtp_config = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'alerts@heliobio.social',
            'password': 'your_password',
            'from': 'alerts@heliobio.social',
            'to': ['admin@heliobio.social', 'research@heliobio.social']
        }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value}] {alert.title}"
            msg['From'] = smtp_config['from']
            msg['To'] = ', '.join(smtp_config['to'])
            
            # Crear contenido HTML
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert-critical {{ background-color: #ffcccc; border-left: 5px solid #ff0000; padding: 15px; }}
                    .alert-high {{ background-color: #ffe6cc; border-left: 5px solid #ff6600; padding: 15px; }}
                    .alert-moderate {{ background-color: #ffffcc; border-left: 5px solid #ffcc00; padding: 15px; }}
                    .data-table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    .data-table th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="alert-{alert.severity.value.lower()}">
                    <h2>🚨 {alert.title}</h2>
                    <p><strong>Severidad:</strong> {alert.severity.value}</p>
                    <p><strong>Tipo:</strong> {alert.type.value}</p>
                    <p><strong>Hora:</strong> {alert.timestamp}</p>
                    <p>{alert.message}</p>
                </div>
                
                <h3>Datos de la Alerta:</h3>
                <table class="data-table">
                    <tr><th>Campo</th><th>Valor</th></tr>
            """
            
            for key, value in alert.data.items():
                html += f"<tr><td>{key}</td><td>{value}</td></tr>"
            
            html += """
                </table>
                
                <p><em>Esta alerta fue generada automáticamente por HelioBio-Social Alert System</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Enviar email
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
                
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Enviar notificación a webhook"""
        # Configuración de webhook (debería venir de variables de entorno)
        webhook_url = "https://hooks.example.com/alerts"
        
        payload = {
            'alert': alert.to_dict(),
            'system': 'HelioBio-Social',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook notification sent for alert {alert.id}")
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Enviar notificación a Slack"""
        # Configuración de Slack (debería venir de variables de entorno)
        slack_webhook = "https://hooks.slack.com/services/..."
        
        # Determinar color según severidad
        color_map = {
            AlertSeverity.CRITICAL: "#ff0000",
            AlertSeverity.HIGH: "#ff6600",
            AlertSeverity.MODERATE: "#ffcc00",
            AlertSeverity.LOW: "#3366ff",
            AlertSeverity.INFO: "#00cc00"
        }
        
        payload = {
            'attachments': [{
                'color': color_map.get(alert.severity, "#cccccc"),
                'title': f"🚨 {alert.title}",
                'text': alert.message,
                'fields': [
                    {
                        'title': 'Severidad',
                        'value': alert.severity.value,
                        'short': True
                    },
                    {
                        'title': 'Tipo',
                        'value': alert.type.value,
                        'short': True
                    },
                    {
                        'title': 'Timestamp',
                        'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'short': False
                    }
                ],
                'footer': 'HelioBio-Social Alert System',
                'ts': datetime.now().timestamp()
            }]
        }
        
        try:
            response = requests.post(
                slack_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent for alert {alert.id}")
            else:
                logger.error(f"Slack webhook failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def _clean_expired_alerts(self):
        """Limpiar alertas expiradas de active_alerts"""
        now = datetime.now()
        expired_ids = []
        
        for alert_id, alert in self.active_alerts.items():
            if alert.expires_at and alert.expires_at < now:
                expired_ids.append(alert_id)
        
        for alert_id in expired_ids:
            del self.active_alerts[alert_id]
            logger.info(f"Expired alert removed: {alert_id}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Obtener alertas activas, opcionalmente filtradas por severidad"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return [alert.to_dict() for alert in alerts]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de alertas"""
        recent_history = self.alert_history[-limit:] if self.alert_history else []
        return [alert.to_dict() for alert in recent_history]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Marcar alerta como reconocida"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de alertas"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        alerts_last_24h = [
            a for a in self.alert_history 
            if a.timestamp > last_24h
        ]
        
        by_severity = {}
        by_type = {}
        
        for alert in alerts_last_24h:
            # Conteo por severidad
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Conteo por tipo
            alert_type = alert.type.value
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
        
        return {
            'total_alerts': len(self.alert_history),
            'active_alerts': len(self.active_alerts),
            'alerts_last_24h': len(alerts_last_24h),
            'by_severity': by_severity,
            'by_type': by_type,
            'rules_registered': len(self.rules)
        }

# Singleton global
alert_engine = AlertEngine(notification_channels=['log', 'email'])
