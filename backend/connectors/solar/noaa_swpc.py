"""
Conector para datos de actividad solar de NOAA Space Weather Prediction Center
API pública: https://services.swpc.noaa.gov/
"""
import httpx
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SolarData:
    """Estructura para datos solares normalizados"""
    timestamp: datetime
    kp_index: float
    ap_index: float
    solar_wind_speed: float  # km/s
    solar_wind_density: float  # protons/cm³
    bt: float  # Campo magnético interplanetario total (nT)
    bz: float  # Componente Bz (nT) - crucial para efectos en Tierra
    sunspot_number: Optional[float] = None
    flare_index: Optional[float] = None
    proton_flux: Optional[float] = None

class NOAAConnector:
    """Cliente para APIs de NOAA Space Weather"""
    
    BASE_URL = "https://services.swpc.noaa.gov"
    
    def __init__(self, cache_ttl: int = 300):
        """Inicializar conector NOAA
        
        Args:
            cache_ttl: Tiempo de vida de caché en segundos
        """
        self.cache_ttl = cache_ttl
        self._cache = {}
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_realtime_data(self) -> SolarData:
        """Obtener datos en tiempo real (última hora)"""
        try:
            # 1. Índice Kp actual (3 horas)
            kp_url = f"{self.BASE_URL}/products/noaa-planetary-k-index.json"
            kp_response = await self.session.get(kp_url)
            kp_data = kp_response.json()
            
            # 2. Viento solar (ACE/DSCOVR)
            solar_wind_url = f"{self.BASE_URL}/json/ace/swepam.json"
            wind_response = await self.session.get(solar_wind_url)
            wind_data = wind_response.json()
            
            # 3. Campo magnético interplanetario
            mag_url = f"{self.BASE_URL}/json/ace/mag.json"
            mag_response = await self.session.get(mag_url)
            mag_data = mag_response.json()
            
            # Procesar datos
            latest_kp = kp_data[-1] if kp_data else {}
            latest_wind = wind_data[-1] if wind_data else {}
            latest_mag = mag_data[-1] if mag_data else {}
            
            return SolarData(
                timestamp=datetime.utcnow(),
                kp_index=float(latest_kp.get('kp_index', 0)),
                ap_index=float(latest_kp.get('ap_index', 0)),
                solar_wind_speed=float(latest_wind.get('speed', 0)),
                solar_wind_density=float(latest_wind.get('density', 0)),
                bt=float(latest_mag.get('bt', 0)),
                bz=float(latest_mag.get('bz', 0))
            )
            
        except Exception as e:
            logger.error(f"Error fetching NOAA realtime data: {e}")
            raise
    
    async def fetch_historical_kp(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Obtener datos históricos del índice Kp"""
        try:
            # Formatear fechas para URL NOAA
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            url = f"{self.BASE_URL}/products/noaa-planetary-k-index.json"
            response = await self.session.get(url)
            data = response.json()
            
            # Convertir a DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['time_tag'])
            
            # Filtrar por rango de fechas
            mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
            return df[mask].copy()
            
        except Exception as e:
            logger.error(f"Error fetching historical Kp data: {e}")
            raise
    
    async def fetch_sunspot_data(self, months: int = 12) -> pd.DataFrame:
        """Obtener datos de manchas solares históricos"""
        try:
            url = f"{self.BASE_URL}/json/sunspots/sunspots.json"
            response = await self.session.get(url)
            data = response.json()
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['time-tag'])
            
            # Filtrar últimos N meses
            cutoff_date = datetime.utcnow() - timedelta(days=months*30)
            return df[df['timestamp'] >= cutoff_date].copy()
            
        except Exception as e:
            logger.error(f"Error fetching sunspot data: {e}")
            raise
    
    async def check_geomagnetic_storm(self, kp_threshold: float = 5.0) -> Dict[str, Any]:
        """Verificar si hay tormenta geomagnética activa"""
        try:
            data = await self.fetch_realtime_data()
            
            storm_level = "NONE"
            if data.kp_index >= 7:
                storm_level = "SEVERE"
            elif data.kp_index >= 6:
                storm_level = "STRONG"
            elif data.kp_index >= 5:
                storm_level = "MODERATE"
            
            return {
                "storm_active": data.kp_index >= kp_threshold,
                "storm_level": storm_level,
                "kp_index": data.kp_index,
                "bz_orientation": "SOUTH" if data.bz < 0 else "NORTH",
                "solar_wind_speed": data.solar_wind_speed,
                "timestamp": data.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking geomagnetic storm: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Cerrar sesión HTTP"""
        await self.session.aclose()

# Singleton para uso global
noaa_connector = NOAAConnector()
