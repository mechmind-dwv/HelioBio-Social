"""
Conector para Google Trends usando pytrends
Instalar: pip install pytrends
"""
import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Any
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

class GoogleTrendsConnector:
    """Conector para datos de Google Trends"""
    
    def __init__(self, hl: str = 'en-US', tz: int = 360, timeout: int = 30):
        """Inicializar cliente de Google Trends
        
        Args:
            hl: Idioma (es para español)
            tz: Zona horaria (360 = CST)
            timeout: Timeout en segundos
        """
        self.pytrends = TrendReq(hl=hl, tz=tz, timeout=timeout)
        self._cache = {}
    
    async def get_trends_for_keywords(self, keywords: List[str], 
                                     timeframe: str = 'today 12-m',
                                     geo: str = '') -> pd.DataFrame:
        """Obtener tendencias para palabras clave específicas"""
        try:
            # Construir payload
            self.pytrends.build_payload(
                kw_list=keywords,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            # Obtener datos de interés por tiempo
            df = self.pytrends.interest_over_time()
            
            if not df.empty:
                # Eliminar columna 'isPartial' si existe
                if 'isPartial' in df.columns:
                    df = df.drop('isPartial', axis=1)
                
                return df
            else:
                logger.warning(f"No data found for keywords: {keywords}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching Google Trends data: {e}")
            return pd.DataFrame()
    
    async def get_mental_health_trends(self, 
                                      timeframe: str = 'today 12-m',
                                      geo: str = '') -> Dict[str, Any]:
        """Obtener tendencias para términos de salud mental"""
        # Términos clave de salud mental (en inglés por defecto)
        mental_health_keywords = [
            'depression',
            'anxiety', 
            'stress',
            'suicide',
            'therapy',
            'mental health',
            'bipolar',
            'panic attack'
        ]
        
        try:
            df = await self.get_trends_for_keywords(
                keywords=mental_health_keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            if not df.empty:
                # Calcular estadísticas
                stats = {
                    'overall_trend': df.mean().to_dict(),
                    'peak_periods': {},
                    'correlation_matrix': df.corr().to_dict(),
                    'total_samples': len(df)
                }
                
                # Encontrar picos para cada término
                for keyword in mental_health_keywords:
                    if keyword in df.columns:
                        series = df[keyword]
                        peak_idx = series.idxmax()
                        peak_value = series.max()
                        stats['peak_periods'][keyword] = {
                            'date': peak_idx.strftime('%Y-%m-%d'),
                            'value': float(peak_value)
                        }
                
                return {
                    'data': df.reset_index().to_dict('records'),
                    'statistics': stats,
                    'keywords': mental_health_keywords,
                    'timeframe': timeframe,
                    'geo': geo if geo else 'Worldwide'
                }
            else:
                return {'error': 'No data available'}
                
        except Exception as e:
            logger.error(f"Error fetching mental health trends: {e}")
            return {'error': str(e)}
    
    async def get_related_queries(self, keyword: str, 
                                 timeframe: str = 'today 12-m',
                                 geo: str = '') -> Dict[str, List]:
        """Obtener consultas relacionadas"""
        try:
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe=timeframe,
                geo=geo
            )
            
            related_queries = self.pytrends.related_queries()
            
            if keyword in related_queries:
                top_queries = related_queries[keyword].get('top', pd.DataFrame())
                rising_queries = related_queries[keyword].get('rising', pd.DataFrame())
                
                return {
                    'top_queries': top_queries.to_dict('records') if not top_queries.empty else [],
                    'rising_queries': rising_queries.to_dict('records') if not rising_queries.empty else []
                }
            else:
                return {'top_queries': [], 'rising_queries': []}
                
        except Exception as e:
            logger.error(f"Error fetching related queries: {e}")
            return {'error': str(e)}
    
    @lru_cache(maxsize=128)
    def get_cached_trends(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Obtener datos de tendencias desde caché"""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            # Verificar si el caché es válido (menos de 1 hora)
            if datetime.now() - timestamp < timedelta(hours=1):
                return data
        return None
    
    def set_cached_trends(self, cache_key: str, data: pd.DataFrame):
        """Guardar datos en caché"""
        self._cache[cache_key] = (data, datetime.now())

# Singleton global
trends_connector = GoogleTrendsConnector()
