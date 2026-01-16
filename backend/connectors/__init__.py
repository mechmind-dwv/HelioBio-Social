"""
Conectores para APIs externas de HelioBio-Social
"""

from .solar.noaa_swpc import NOAAConnector, noaa_connector, SolarData
from .health.who_gho import WHOConnector, who_connector, WHOMentalHealthIndicator
from .social.google_trends import GoogleTrendsConnector, trends_connector

# Exportar todas las clases principales
__all__ = [
    'NOAAConnector',
    'noaa_connector',
    'SolarData',
    'WHOConnector', 
    'who_connector',
    'WHOMentalHealthIndicator',
    'GoogleTrendsConnector',
    'trends_connector'
]

# Diccionario de conectores disponibles
CONNECTORS = {
    'solar': {
        'noaa': noaa_connector,
        'description': 'NOAA Space Weather Prediction Center'
    },
    'health': {
        'who': who_connector,
        'description': 'World Health Organization Global Health Observatory'
    },
    'social': {
        'google_trends': trends_connector,
        'description': 'Google Trends API'
    }
}

def get_connector(connector_type: str, connector_name: str):
    """Obtener conector por tipo y nombre"""
    try:
        return CONNECTORS[connector_type][connector_name]
    except KeyError:
        raise ValueError(f"Connector {connector_name} of type {connector_type} not found")
