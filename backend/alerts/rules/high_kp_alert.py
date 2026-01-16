"""
Reglas específicas para alertas de alta actividad solar (Kp)
"""
from ..alert_engine import AlertRule, AlertType, AlertSeverity
from datetime import datetime, timedelta

def create_high_kp_rules():
    """Crear reglas para alta actividad solar Kp"""
    
    rules = []
    
    # 1. Regla para Kp > 5 (Tormenta geomagnética menor)
    def kp_greater_than_5(data: Dict[str, Any]) -> bool:
        kp = data.get('kp_index', 0)
        return kp >= 5.0
    
    rules.append(AlertRule(
        name="kp_minor_storm",
        condition=kp_greater_than_5,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.LOW,
        message_template="Tormenta geomagnética menor detectada: Kp={kp_index:.1f}. "
                       "Puede haber efectos leves en sistemas sensibles.",
        cooldown_minutes=180
    ))
    
    # 2. Regla para Kp > 6 (Tormenta moderada-fuerte)
    def kp_greater_than_6(data: Dict[str, Any]) -> bool:
        kp = data.get('kp_index', 0)
        bz = data.get('bz', 0)
        
        # Más probable que cause efectos si Bz es negativo (sur)
        return kp >= 6.0 and bz < 0
    
    rules.append(AlertRule(
        name="kp_moderate_storm_bz_south",
        condition=kp_greater_than_6,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.MODERATE,
        message_template="Tormenta geomagnética moderada-fuerte: Kp={kp_index:.1f}, Bz={bz:.1f}nT (SUR). "
                       "Altamente probable ver efectos en salud mental en 3-5 días.",
        cooldown_minutes=120
    ))
    
    # 3. Regla para Kp > 7 (Tormenta severa)
    def kp_greater_than_7(data: Dict[str, Any]) -> bool:
        kp = data.get('kp_index', 0)
        solar_wind = data.get('solar_wind_speed', 0)
        
        return kp >= 7.0 and solar_wind > 600
    
    rules.append(AlertRule(
        name="kp_severe_storm",
        condition=kp_greater_than_7,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.HIGH,
        message_template="⚠️ TORMENTA GEOMAGNÉTICA SEVERA: Kp={kp_index:.1f}, "
                       "Viento solar={solar_wind_speed:.0f}km/s. "
                       "Esperar efectos significativos. Revisar protocolos de alerta.",
        cooldown_minutes=60
    ))
    
    # 4. Regla para Kp > 8 (Tormenta extrema)
    def kp_greater_than_8(data: Dict[str, Any]) -> bool:
        kp = data.get('kp_index', 0)
        return kp >= 8.0
    
    rules.append(AlertRule(
        name="kp_extreme_storm",
        condition=kp_greater_than_8,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.CRITICAL,
        message_template="🚨🚨 TORMENTA GEOMAGNÉTICA EXTREMA: Kp={kp_index:.1f}. "
                       "EMERGENCIA. Efectos globales esperados. "
                       "Activar todos los protocolos de respuesta.",
        cooldown_minutes=30
    ))
    
    # 5. Regla para aumento rápido de Kp
    def rapid_kp_increase(data: Dict[str, Any]) -> bool:
        kp_current = data.get('kp_current', 0)
        kp_3h_ago = data.get('kp_3h_ago', 0)
        
        # Aumento de 2 puntos o más en 3 horas
        return kp_current - kp_3h_ago >= 2.0
    
    rules.append(AlertRule(
        name="rapid_kp_increase",
        condition=rapid_kp_increase,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.MODERATE,
        message_template="Aumento rápido de Kp detectado: {kp_3h_ago:.1f} → {kp_current:.1f} "
                       "(Δ={kp_increase:.1f}) en 3 horas. Preparar para posible tormenta.",
        cooldown_minutes=90
    ))
    
    return rules

def create_solar_parameter_rules():
    """Reglas basadas en otros parámetros solares"""
    
    rules = []
    
    # 1. Regla para alta densidad de protones
    def high_proton_density(data: Dict[str, Any]) -> bool:
        density = data.get('proton_density', 0)
        return density >= 10.0  # partículas/cm³
    
    rules.append(AlertRule(
        name="high_proton_density",
        condition=high_proton_density,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.LOW,
        message_template="Alta densidad de protones: {proton_density:.1f} p/cm³. "
                       "Puede indicar CME aproximándose.",
        cooldown_minutes=240
    ))
    
    # 2. Regla para viento solar rápido
    def fast_solar_wind(data: Dict[str, Any]) -> bool:
        speed = data.get('solar_wind_speed', 0)
        return speed >= 700  # km/s
    
    rules.append(AlertRule(
        name="fast_solar_wind",
        condition=fast_solar_wind,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.MODERATE,
        message_template="Viento solar rápido detectado: {solar_wind_speed:.0f} km/s. "
                       "Puede desencadenar actividad geomagnética.",
        cooldown_minutes=180
    ))
    
    # 3. Regla para Bz fuertemente negativo
    def strong_negative_bz(data: Dict[str, Any]) -> bool:
        bz = data.get('bz', 0)
        return bz <= -10  # nT
    
    rules.append(AlertRule(
        name="strong_negative_bz",
        condition=strong_negative_bz,
        alert_type=AlertType.GEOMAGNETIC_STORM,
        severity=AlertSeverity.HIGH,
        message_template="Bz fuertemente negativo: {bz:.1f} nT (SUR). "
                       "Condición ideal para tormentas geomagnéticas intensas.",
        cooldown_minutes=120
    ))
    
    return rules
