"""
🌞 SERVICIO DE DATOS SOLARES REALES - VERSIÓN CORREGIDA
"""
import aiohttp
import asyncio
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class RealSolarService:
    """Servicio corregido para datos solares realistas"""
    
    def __init__(self):
        self.initialized = False
        
    async def get_current_solar_data(self) -> dict:
        """Obtener datos solares con simulación mejorada del ciclo 25"""
        try:
            # Datos basados en el ciclo solar 25 real
            solar_data = await self.get_enhanced_simulation()
            self.initialized = True
            return solar_data
            
        except Exception as e:
            logger.error(f"Error en servicio solar: {e}")
            return await self.get_fallback_data()
    
    async def get_enhanced_simulation(self) -> dict:
        """Simulación mejorada basada en ciclo solar 25 real"""
        current_date = datetime.now()
        
        # Ciclo solar 25 (2020-2031) - Datos realistas
        cycle_data = self._get_current_cycle_data(current_date)
        
        # Variación diaria realista
        daily_variation = random.uniform(-0.15, 0.15)
        sunspots = max(10, int(cycle_data['base_sunspots'] * (1 + daily_variation)))
        
        # Otras métricas correlacionadas
        flare_activity = self._calculate_flare_activity(sunspots)
        geomagnetic_storm = self._calculate_geomagnetic_activity(sunspots)
        
        return {
            'sunspot_number': sunspots,
            'solar_flux': 70.0 + (sunspots / 2),
            'flare_activity': flare_activity,
            'geomagnetic_storm': geomagnetic_storm,
            'solar_wind_speed': 400 + random.randint(-50, 100),
            'coronal_holes': random.randint(0, 3),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'enhanced_simulation',
            'solar_cycle_phase': cycle_data['phase'],
            'cycle_progress': cycle_data['progress']
        }
    
    def _get_current_cycle_data(self, current_date: datetime) -> dict:
        """Calcular datos del ciclo solar 25 actual"""
        cycle_start = 2020
        cycle_duration = 11  # años
        
        current_year = current_date.year
        current_month = current_date.month
        
        # Progreso del ciclo (0-1)
        cycle_progress = (current_year - cycle_start) / cycle_duration
        
        # Fase del ciclo
        if cycle_progress < 0.3:
            phase = "early_ascending"
            base_sunspots = 20 + (cycle_progress * 120)  # 20-56
        elif cycle_progress < 0.6:
            phase = "late_ascending" 
            base_sunspots = 56 + ((cycle_progress - 0.3) * 94)  # 56-150
        elif cycle_progress < 0.8:
            phase = "maximum"
            base_sunspots = 150 - ((cycle_progress - 0.6) * 70)  # 150-80
        else:
            phase = "descending"
            base_sunspots = 80 - ((cycle_progress - 0.8) * 60)  # 80-20
        
        # Ajuste mensual para variación
        monthly_adjustment = (current_month - 6) / 6.0  # ±16%
        base_sunspots *= (1 + monthly_adjustment * 0.16)
        
        return {
            'base_sunspots': base_sunspots,
            'phase': phase,
            'progress': cycle_progress
        }
    
    def _calculate_flare_activity(self, sunspots: int) -> int:
        """Calcular actividad de fulguraciones basada en manchas solares"""
        if sunspots > 120:
            return random.choices([3, 4, 5], weights=[0.3, 0.4, 0.3])[0]
        elif sunspots > 80:
            return random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
        elif sunspots > 40:
            return random.choices([1, 2, 3], weights=[0.5, 0.4, 0.1])[0]
        else:
            return random.choices([0, 1], weights=[0.7, 0.3])[0]
    
    def _calculate_geomagnetic_activity(self, sunspots: int) -> int:
        """Calcular actividad geomagnética"""
        if sunspots > 100:
            return random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
        elif sunspots > 60:
            return random.choices([1, 2, 3], weights=[0.5, 0.4, 0.1])[0]
        else:
            return random.choices([0, 1], weights=[0.8, 0.2])[0]
    
    async def get_fallback_data(self) -> dict:
        """Datos de fallback"""
        return {
            'sunspot_number': 45 + random.randint(-15, 15),
            'solar_flux': 72.5 + random.uniform(-10, 10),
            'flare_activity': random.randint(0, 5),
            'geomagnetic_storm': random.randint(0, 4),
            'solar_wind_speed': 400 + random.randint(-50, 50),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'fallback_simulation'
        }
