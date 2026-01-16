"""
Conector para datos de salud mental de la Organización Mundial de la Salud
Global Health Observatory (GHO) API
API: https://www.who.int/data/gho
"""
import httpx
import pandas as pd
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class WHOMentalHealthIndicator(Enum):
    """Indicadores de salud mental de la OMS"""
    SUICIDE_RATES = "MH_12"  # Tasas de suicidio por 100k
    DEPRESSION_PREVALENCE = "MH_2"  # Prevalencia de depresión
    ANXIETY_PREVALENCE = "MH_3"  # Prevalencia de ansiedad
    BIPOLAR_PREVALENCE = "MH_4"  # Prevalencia de trastorno bipolar
    SCHIZOPHRENIA_PREVALENCE = "MH_5"  # Prevalencia de esquizofrenia
    ALCOHOL_USE_DISORDERS = "SA_1"  # Trastornos por uso de alcohol
    DRUG_USE_DISORDERS = "SA_2"  # Trastornos por uso de drogas

class WHOConnector:
    """Cliente para API de la Organización Mundial de la Salud"""
    
    BASE_URL = "https://ghoapi.azureedge.net/api"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=60.0)
        self._cache = {}
    
    async def get_indicator_data(self, indicator: WHOMentalHealthIndicator, 
                                country_code: Optional[str] = None,
                                year: Optional[int] = None) -> pd.DataFrame:
        """Obtener datos de un indicador específico"""
        try:
            # Construir URL
            url = f"{self.BASE_URL}/{indicator.value}"
            params = {}
            
            if country_code:
                params['$filter'] = f"SpatialDim eq '{country_code}'"
            if year:
                if params.get('$filter'):
                    params['$filter'] += f" and TimeDim eq {year}"
                else:
                    params['$filter'] = f"TimeDim eq {year}"
            
            logger.info(f"Fetching WHO data from: {url}")
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('value', [])
                
                if records:
                    df = pd.DataFrame(records)
                    # Limpiar nombres de columnas
                    df.columns = [col.lower().replace('dim', '') for col in df.columns]
                    return df
                else:
                    logger.warning(f"No data found for indicator {indicator}")
                    return pd.DataFrame()
            else:
                logger.error(f"WHO API error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching WHO indicator data: {e}")
            return pd.DataFrame()
    
    async def get_suicide_rates(self, country_code: str = None, 
                               start_year: int = 2000, 
                               end_year: int = 2023) -> pd.DataFrame:
        """Obtener tasas de suicidio por país y año"""
        try:
            all_data = []
            
            for year in range(start_year, end_year + 1):
                df = await self.get_indicator_data(
                    WHOMentalHealthIndicator.SUICIDE_RATES,
                    country_code=country_code,
                    year=year
                )
                
                if not df.empty:
                    # Extraer valor numérico
                    df['suicide_rate'] = pd.to_numeric(df['numericvalue'], errors='coerce')
                    df['year'] = year
                    
                    # Seleccionar columnas relevantes
                    cols_to_keep = ['spatialdim', 'year', 'suicide_rate']
                    cols_to_keep = [col for col in cols_to_keep if col in df.columns]
                    all_data.append(df[cols_to_keep])
            
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching suicide rates: {e}")
            return pd.DataFrame()
    
    async def get_mental_health_burden(self, country_code: str = "GLOBAL") -> Dict[str, Any]:
        """Obtener carga de enfermedad mental (DALYs)"""
        try:
            # Para carga de enfermedad, necesitamos múltiples indicadores
            indicators = {
                'depression': WHOMentalHealthIndicator.DEPRESSION_PREVALENCE,
                'anxiety': WHOMentalHealthIndicator.ANXIETY_PREVALENCE,
                'bipolar': WHOMentalHealthIndicator.BIPOLAR_PREVALENCE,
                'schizophrenia': WHOMentalHealthIndicator.SCHIZOPHRENIA_PREVALENCE
            }
            
            results = {}
            
            for disorder, indicator in indicators.items():
                df = await self.get_indicator_data(
                    indicator,
                    country_code=country_code if country_code != "GLOBAL" else None,
                    year=2023  # Último año disponible
                )
                
                if not df.empty and 'numericvalue' in df.columns:
                    # Calcular promedio
                    try:
                        values = pd.to_numeric(df['numericvalue'], errors='coerce')
                        avg_value = values.mean()
                        results[disorder] = {
                            'prevalence': float(avg_value),
                            'unit': 'percentage' if disorder in ['depression', 'anxiety'] else 'per_100k'
                        }
                    except:
                        results[disorder] = {'prevalence': None, 'unit': 'unknown'}
            
            return {
                'country': country_code,
                'year': 2023,
                'indicators': results,
                'total_burden': sum([v['prevalence'] for v in results.values() if v['prevalence']]),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching mental health burden: {e}")
            return {'error': str(e)}
    
    async def get_country_list(self) -> List[Dict[str, str]]:
        """Obtener lista de países disponibles en GHO"""
        try:
            url = f"{self.BASE_URL}/DIMENSION/COUNTRY/DimensionValues"
            response = await self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                countries = []
                
                for item in data.get('value', []):
                    countries.append({
                        'code': item.get('Code'),
                        'name': item.get('Title'),
                        'region': item.get('ParentDimension', {}).get('Title', '')
                    })
                
                return countries
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching country list: {e}")
            return []
    
    async def close(self):
        """Cerrar sesión HTTP"""
        await self.session.aclose()

# Singleton global
who_connector = WHOConnector()
