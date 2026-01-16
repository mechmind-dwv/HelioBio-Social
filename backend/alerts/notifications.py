"""
Sistema de notificaciones para HelioBio-Social
Maneja envío de alertas por múltiples canales
"""
import asyncio
import smtplib
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime
import requests
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Configuración de notificaciones"""
    email_enabled: bool = False
    sms_enabled: bool = False
    webhook_enabled: bool = False
    slack_enabled: bool = False
    telegram_enabled: bool = False
    
    # Configuración de email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "alerts@heliobio.social"
    email_to: List[str] = None
    
    # Configuración de webhook
    webhook_url: str = ""
    
    # Configuración de Slack
    slack_webhook_url: str = ""
    
    # Configuración de Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    def __post_init__(self):
        if self.email_to is None:
            self.email_to = ["admin@heliobio.social"]

class NotificationService:
    """Servicio de notificaciones"""
    
    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        self.notification_history = []
        
        # Cargar configuración desde variables de entorno
        self._load_from_env()
    
    def _load_from_env(self):
        """Cargar configuración desde variables de entorno"""
        # Email
        if os.getenv('SMTP_HOST'):
            self.config.smtp_host = os.getenv('SMTP_HOST')
        if os.getenv('SMTP_USERNAME'):
            self.config.smtp_username = os.getenv('SMTP_USERNAME')
        if os.getenv('SMTP_PASSWORD'):
            self.config.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Lista de emails desde variable de entorno
        email_list = os.getenv('ALERT_EMAILS', '')
        if email_list:
            self.config.email_to = [email.strip() for email in email_list.split(',')]
        
        # Webhook
        if os.getenv('WEBHOOK_URL'):
            self.config.webhook_url = os.getenv('WEBHOOK_URL')
            self.config.webhook_enabled = True
        
        # Slack
        if os.getenv('SLACK_WEBHOOK_URL'):
            self.config.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            self.config.slack_enabled = True
        
        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.config.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            self.config.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
            self.config.telegram_enabled = bool(self.config.telegram_chat_id)
    
    async def send_alert_notification(self, alert_data: Dict[str, Any], 
                                     channels: List[str] = None) -> Dict[str, bool]:
        """Enviar notificación de alerta por canales especificados"""
        
        if channels is None:
            channels = self._get_enabled_channels()
        
        results = {}
        
        for channel in channels:
            try:
                if channel == 'email' and self.config.email_enabled:
                    success = await self._send_email(alert_data)
                    results['email'] = success
                    
                elif channel == 'webhook' and self.config.webhook_enabled:
                    success = await self._send_webhook(alert_data)
                    results['webhook'] = success
                    
                elif channel == 'slack' and self.config.slack_enabled:
                    success = await self._send_slack(alert_data)
                    results['slack'] = success
                    
                elif channel == 'telegram' and self.config.telegram_enabled:
                    success = await self._send_telegram(alert_data)
                    results['telegram'] = success
                    
                elif channel == 'log':
                    self._send_log(alert_data)
                    results['log'] = True
                    
                else:
                    logger.warning(f"Channel {channel} not enabled or not supported")
                    results[channel] = False
                    
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
                results[channel] = False
        
        # Registrar en historial
        self.notification_history.append({
            'timestamp': datetime.now(),
            'alert_id': alert_data.get('id'),
            'channels': channels,
            'results': results,
            'alert_data': alert_data
        })
        
        return results
    
    def _get_enabled_channels(self) -> List[str]:
        """Obtener lista de canales habilitados"""
        channels = ['log']  # Siempre log
        
        if self.config.email_enabled and self.config.smtp_username:
            channels.append('email')
        if self.config.webhook_enabled and self.config.webhook_url:
            channels.append('webhook')
        if self.config.slack_enabled and self.config.slack_webhook_url:
            channels.append('slack')
        if self.config.telegram_enabled and self.config.telegram_bot_token:
            channels.append('telegram')
        
        return channels
    
    async def _send_email(self, alert_data: Dict[str, Any]) -> bool:
        """Enviar notificación por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_email_subject(alert_data)
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            
            # Crear contenido
            html_content = self._create_email_html(alert_data)
            text_content = self._create_email_text(alert_data)
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar usando aiosmtplib (async)
            await aiosmtplib.send(
                msg,
                hostname=self.config.smtp_host,
                port=self.config.smtp_port,
                username=self.config.smtp_username,
                password=self.config.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email notification sent for alert {alert_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _create_email_subject(self, alert_data: Dict[str, Any]) -> str:
        """Crear asunto del email"""
        severity = alert_data.get('severity', 'UNKNOWN')
        alert_type = alert_data.get('type', 'ALERT')
        title = alert_data.get('title', '')
        
        emoji = {
            'CRITICAL': '🚨🚨',
            'HIGH': '🚨',
            'MODERATE': '⚠️',
            'LOW': '🔔',
            'INFO': 'ℹ️'
        }.get(severity, '📧')
        
        return f"{emoji} [{severity}] {alert_type}: {title}"
    
    def _create_email_html(self, alert_data: Dict[str, Any]) -> str:
        """Crear contenido HTML del email"""
        
        # Mapa de colores según severidad
        color_map = {
            'CRITICAL': '#ff0000',
            'HIGH': '#ff6600',
            'MODERATE': '#ffcc00',
            'LOW': '#3366ff',
            'INFO': '#00cc00'
        }
        
        severity = alert_data.get('severity', 'UNKNOWN')
        bg_color = color_map.get(severity, '#cccccc')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>HelioBio-Social Alert</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .alert-header {{
                    background-color: {bg_color};
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    margin-bottom: 0;
                }}
                .alert-content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                }}
                .severity-badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    background-color: {bg_color};
                    color: white;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .data-table th {{
                    background-color: #f2f2f2;
                    text-align: left;
                    padding: 12px;
                    border: 1px solid #ddd;
                }}
                .data-table td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 0.9em;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 0.9em;
                }}
                @media (max-width: 600px) {{
                    .data-table {{
                        font-size: 0.9em;
                    }}
                    .data-table th, .data-table td {{
                        padding: 8px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="alert-header">
                <h1 style="margin: 0;">🚨 HelioBio-Social Alert System</h1>
            </div>
            
            <div class="alert-content">
                <h2>{alert_data.get('title', 'Alert')}</h2>
                
                <div>
                    <span class="severity-badge">{severity}</span>
                    <span><strong>Type:</strong> {alert_data.get('type', 'N/A')}</span>
                </div>
                
                <p class="timestamp">
                    <strong>Timestamp:</strong> {alert_data.get('timestamp', 'N/A')}
                </p>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #fff; border-left: 4px solid {bg_color};">
                    <p style="margin: 0; font-size: 1.1em;"><strong>Message:</strong><br>
                    {alert_data.get('message', 'No message provided')}</p>
                </div>
                
                <h3>Alert Data:</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Agregar datos de la alerta
        for key, value in alert_data.get('data', {}).items():
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, indent=2)
            html += f"""
                        <tr>
                            <td><strong>{key}</strong></td>
                            <td>{value}</td>
                        </tr>
            """
        
        html += f"""
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>
                        <strong>Alert ID:</strong> {alert_data.get('id', 'N/A')}<br>
                        <strong>Generated by:</strong> HelioBio-Scientific Alert System<br>
                        <strong>System:</strong> Solar-Mental Health Correlation Monitor
                    </p>
                    <p style="font-size: 0.8em;">
                        This is an automated message. Please do not reply to this email.<br>
                        To manage your alert preferences, visit the HelioBio-Social dashboard.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_email_text(self, alert_data: Dict[str, Any]) -> str:
        """Crear contenido de texto plano para email"""
        text = f"""
        HELIOBIO-SOCIAL ALERT SYSTEM
        {'=' * 50}
        
        ALERT: {alert_data.get('title', 'Unknown Alert')}
        
        Severity: {alert_data.get('severity', 'UNKNOWN')}
        Type: {alert_data.get('type', 'UNKNOWN')}
        Timestamp: {alert_data.get('timestamp', 'N/A')}
        Alert ID: {alert_data.get('id', 'N/A')}
        
        MESSAGE:
        {alert_data.get('message', 'No message provided')}
        
        {'=' * 50}
        
        ALERT DATA:
        """
        
        for key, value in alert_data.get('data', {}).items():
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, indent=2)
            text += f"\n{key}: {value}"
        
        text += f"""
        
        {'=' * 50}
        
        This is an automated alert from the HelioBio-Social system.
        Solar-Mental Health Correlation Monitoring System.
        
        For more information or to manage alerts, visit the dashboard.
        """
        
        return text
    
    async def _send_webhook(self, alert_data: Dict[str, Any]) -> bool:
        """Enviar notificación a webhook"""
        try:
            response = await asyncio.to_thread(
                requests.post,
                self.config.webhook_url,
                json=alert_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Webhook notification sent successfully for alert {alert_data.get('id')}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    async def _send_slack(self, alert_data: Dict[str, Any]) -> bool:
        """Enviar notificación a Slack"""
        try:
            # Determinar color según severidad
            color_map = {
                'CRITICAL': '#ff0000',
                'HIGH': '#ff6600',
                'MODERATE': '#ffcc00',
                'LOW': '#3366ff',
                'INFO': '#00cc00'
            }
            
            severity = alert_data.get('severity', 'UNKNOWN')
            color = color_map.get(severity, '#cccccc')
            
            # Crear payload de Slack
            slack_payload = {
                'attachments': [{
                    'color': color,
                    'title': f"🚨 {alert_data.get('title', 'HelioBio-Social Alert')}",
                    'text': alert_data.get('message', ''),
                    'fields': [
                        {
                            'title': 'Severity',
                            'value': severity,
                            'short': True
                        },
                        {
                            'title': 'Type',
                            'value': alert_data.get('type', 'UNKNOWN'),
                            'short': True
                        },
                        {
                            'title': 'Timestamp',
                            'value': alert_data.get('timestamp', ''),
                            'short': False
                        },
                        {
                            'title': 'Alert ID',
                            'value': alert_data.get('id', ''),
                            'short': False
                        }
                    ],
                    'footer': 'HelioBio-Social Alert System',
                    'ts': datetime.now().timestamp()
                }]
            }
            
            # Agregar datos adicionales si existen
            if alert_data.get('data'):
                data_field = {
                    'title': 'Alert Data',
                    'value': json.dumps(alert_data['data'], indent=2),
                    'short': False
                }
                slack_payload['attachments'][0]['fields'].append(data_field)
            
            response = await asyncio.to_thread(
                requests.post,
                self.config.slack_webhook_url,
                json=slack_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent for alert {alert_data.get('id')}")
                return True
            else:
                logger.error(f"Slack failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Slack error: {e}")
            return False
    
    async def _send_telegram(self, alert_data: Dict[str, Any]) -> bool:
        """Enviar notificación a Telegram"""
        try:
            # Formatear mensaje para Telegram
            message = self._format_telegram_message(alert_data)
            
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.config.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = await asyncio.to_thread(
                requests.post,
                url,
                json=payload,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Telegram notification sent for alert {alert_data.get('id')}")
                return True
            else:
                logger.error(f"Telegram error: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def _format_telegram_message(self, alert_data: Dict[str, Any]) -> str:
        """Formatear mensaje para Telegram"""
        severity = alert_data.get('severity', 'UNKNOWN')
        
        # Emojis según severidad
        emoji_map = {
            'CRITICAL': '🔴🔴',
            'HIGH': '🔴',
            'MODERATE': '🟡',
            'LOW': '🔵',
            'INFO': '🟢'
        }
        
        emoji = emoji_map.get(severity, '⚪')
        
        message = f"""
        {emoji} <b>HELIOBIO-SOCIAL ALERT</b>
        
        <b>Title:</b> {alert_data.get('title', 'N/A')}
        <b>Severity:</b> {severity}
        <b>Type:</b> {alert_data.get('type', 'N/A')}
        <b>Time:</b> {alert_data.get('timestamp', 'N/A')}
        <b>ID:</b> {alert_data.get('id', 'N/A')}
        
        <b>Message:</b>
        {alert_data.get('message', 'No message')}
        
        <i>Automated alert from HelioBio-Social Correlation System</i>
        """
        
        return message
    
    def _send_log(self, alert_data: Dict[str, Any]):
        """Registrar alerta en log"""
        logger.warning(f"""
        📢 ALERT NOTIFICATION
        ID: {alert_data.get('id')}
        Title: {alert_data.get('title')}
        Severity: {alert_data.get('severity')}
        Message: {alert_data.get('message')}
        Data: {json.dumps(alert_data.get('data'), indent=2)}
        """)
    
    def get_notification_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener estadísticas de notificaciones"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [n for n in self.notification_history if n['timestamp'] > cutoff]
        
        stats = {
            'total_notifications': len(self.notification_history),
            'recent_notifications': len(recent),
            'by_channel': {},
            'success_rate': {}
        }
        
        # Analizar canales usados
        for notification in recent:
            for channel, success in notification['results'].items():
                if channel not in stats['by_channel']:
                    stats['by_channel'][channel] = {'total': 0, 'success': 0}
                
                stats['by_channel'][channel]['total'] += 1
                if success:
                    stats['by_channel'][channel]['success'] += 1
        
        # Calcular tasas de éxito
        for channel, data in stats['by_channel'].items():
            if data['total'] > 0:
                stats['success_rate'][channel] = data['success'] / data['total']
        
        return stats

# Singleton global
notification_service = NotificationService()
