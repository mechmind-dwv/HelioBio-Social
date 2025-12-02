"""
NOAA Space Weather Prediction Center (SWPC) API Connector
Retrieves real-time and historical solar activity data
"""
import httpx
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class NOAAConnector:
    """Connector for NOAA SWPC data"""
    
    BASE_URL = "https://services.swpc.noaa.gov"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_kp_index_current(self) -> Dict:
        """
        Get current Kp index (geomagnetic activity)
        Kp ranges from 0 (quiet) to 9 (extreme storm)
        
        Returns:
            dict: {
                'kp': float,
                'timestamp': str (ISO 8601),
                'status': str ('quiet', 'unsettled', 'storm', etc.)
            }
        """
        try:
            url = f"{self.BASE_URL}/products/noaa-planetary-k-index.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Get most recent observation
            if len(data) > 1:
                latest = data[-1]
                timestamp = latest[0]
                kp_value = float(latest[1])
                
                # Classify geomagnetic activity
                status = self._classify_kp(kp_value)
                
                return {
                    'kp': kp_value,
                    'timestamp': timestamp,
                    'status': status,
                    'source': 'NOAA SWPC'
                }
            
            raise ValueError("No Kp data available")
            
        except Exception as e:
            logger.error(f"Error fetching Kp index: {e}")
            raise
    
    async def get_sunspot_number_current(self) -> Dict:
        """
        Get current sunspot number (SSN)
        SSN indicates solar activity level
        
        Returns:
            dict: {
                'ssn': int,
                'timestamp': str,
                'smoothed_ssn': float,
                'solar_cycle_phase': str
            }
        """
        try:
            url = f"{self.BASE_URL}/products/solar-cycle/observed-solar-cycle-indices.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Get most recent observation
            if len(data) > 1:
                latest = data[-1]
                
                return {
                    'ssn': int(latest['ssn']) if latest.get('ssn') else 0,
                    'smoothed_ssn': float(latest['smoothed_ssn']) if latest.get('smoothed_ssn') else 0.0,
                    'timestamp': latest['time-tag'],
                    'solar_cycle_phase': self._classify_solar_cycle(float(latest.get('smoothed_ssn', 0))),
                    'source': 'NOAA SWPC'
                }
            
            raise ValueError("No sunspot data available")
            
        except Exception as e:
            logger.error(f"Error fetching sunspot number: {e}")
            raise
    
    async def get_solar_wind_current(self) -> Dict:
        """
        Get current solar wind measurements
        
        Returns:
            dict: {
                'speed': float (km/s),
                'density': float (protons/cm³),
                'temperature': float (K),
                'timestamp': str
            }
        """
        try:
            url = f"{self.BASE_URL}/products/summary/solar-wind-mag-field.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if 'ACE' in data:
                ace_data = data['ACE']
                return {
                    'speed': float(ace_data.get('Speed', 0)),
                    'density': float(ace_data.get('Density', 0)),
                    'temperature': float(ace_data.get('Temperature', 0)),
                    'timestamp': ace_data.get('TimeTag', ''),
                    'source': 'ACE Satellite (NOAA)'
                }
            
            raise ValueError("No solar wind data available")
            
        except Exception as e:
            logger.error(f"Error fetching solar wind: {e}")
            # Return default values instead of failing
            return {
                'speed': 0.0,
                'density': 0.0,
                'temperature': 0.0,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'NOAA SWPC (unavailable)',
                'error': str(e)
            }
    
    async def get_solar_flares_recent(self, days: int = 7) -> List[Dict]:
        """
        Get recent solar flares
        
        Args:
            days: Number of days to look back
        
        Returns:
            list: List of flare events with classification (X, M, C, B, A)
        """
        try:
            # This is a simplified version - real implementation would use NOAA's event API
            url = f"{self.BASE_URL}/products/solar-flares.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            flares = []
            for event in data:
                if 'class_type' in event and 'begin_time' in event:
                    flares.append({
                        'class': event['class_type'],
                        'begin_time': event['begin_time'],
                        'peak_time': event.get('peak_time', ''),
                        'end_time': event.get('end_time', ''),
                        'location': event.get('location', ''),
                        'intensity': self._flare_to_numeric(event['class_type'])
                    })
            
            return flares
            
        except Exception as e:
            logger.error(f"Error fetching solar flares: {e}")
            return []
    
    async def get_historical_kp(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get historical Kp index data
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with columns: timestamp, kp
        """
        try:
            # NOAA provides historical data in different formats
            # This is a simplified implementation
            url = f"{self.BASE_URL}/products/noaa-planetary-k-index.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=['timestamp', 'kp'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['kp'] = pd.to_numeric(df['kp'])
            
            # Filter by date range
            mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
            df = df[mask]
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical Kp: {e}")
            raise
    
    @staticmethod
    def _classify_kp(kp: float) -> str:
        """Classify geomagnetic activity level"""
        if kp < 3:
            return "quiet"
        elif kp < 4:
            return "unsettled"
        elif kp < 5:
            return "active"
        elif kp < 6:
            return "minor_storm"
        elif kp < 7:
            return "moderate_storm"
        elif kp < 8:
            return "strong_storm"
        elif kp < 9:
            return "severe_storm"
        else:
            return "extreme_storm"
    
    @staticmethod
    def _classify_solar_cycle(ssn: float) -> str:
        """Classify solar cycle phase based on smoothed SSN"""
        if ssn < 30:
            return "minimum"
        elif ssn < 80:
            return "rising"
        elif ssn < 120:
            return "near_maximum"
        elif ssn >= 120:
            return "maximum"
        else:
            return "declining"
    
    @staticmethod
    def _flare_to_numeric(flare_class: str) -> float:
        """Convert flare classification to numeric intensity"""
        if not flare_class:
            return 0.0
        
        class_letter = flare_class[0].upper()
        class_number = float(flare_class[1:]) if len(flare_class) > 1 else 1.0
        
        multipliers = {'X': 10000, 'M': 1000, 'C': 100, 'B': 10, 'A': 1}
        return multipliers.get(class_letter, 0) * class_number


# Example usage and testing
async def main():
    """Test function"""
    async with NOAAConnector() as noaa:
        print("=== Testing NOAA SWPC Connector ===\n")
        
        # Current Kp
        kp_data = await noaa.get_kp_index_current()
        print(f"Current Kp Index: {kp_data['kp']} ({kp_data['status']})")
        print(f"Timestamp: {kp_data['timestamp']}\n")
        
        # Current SSN
        ssn_data = await noaa.get_sunspot_number_current()
        print(f"Current Sunspot Number: {ssn_data['ssn']}")
        print(f"Smoothed SSN: {ssn_data['smoothed_ssn']:.1f}")
        print(f"Solar Cycle Phase: {ssn_data['solar_cycle_phase']}\n")
        
        # Solar Wind
        wind_data = await noaa.get_solar_wind_current()
        print(f"Solar Wind Speed: {wind_data['speed']:.1f} km/s")
        print(f"Proton Density: {wind_data['density']:.2f} p/cm³\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
