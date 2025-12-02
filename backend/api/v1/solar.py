"""
Solar Data API Endpoints
Provides access to current and historical solar activity data
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
import logging

from connectors.solar.noaa_swpc import NOAAConnector
from database import get_db, AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models
class SolarCurrentResponse(BaseModel):
    """Current solar activity snapshot"""
    timestamp: str
    kp_index: float = Field(..., description="Geomagnetic activity (0-9)")
    kp_status: str = Field(..., description="Activity level classification")
    sunspot_number: int = Field(..., description="Current sunspot count")
    smoothed_ssn: float = Field(..., description="11-month smoothed SSN")
    solar_cycle_phase: str = Field(..., description="Current solar cycle phase")
    solar_wind_speed: float = Field(..., description="Solar wind speed (km/s)")
    proton_density: float = Field(..., description="Proton density (p/cm³)")
    data_quality: str = Field(default="good", description="Data quality indicator")


class SolarHistoricalResponse(BaseModel):
    """Historical solar activity data"""
    start_date: str
    end_date: str
    data_points: int
    variables: List[str]
    data: List[dict]


class SolarFlareEvent(BaseModel):
    """Solar flare event"""
    class_type: str = Field(..., description="Flare classification (X, M, C, B, A)")
    intensity: float = Field(..., description="Numeric intensity")
    begin_time: str
    peak_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None


# Endpoints

@router.get("/current", response_model=SolarCurrentResponse)
async def get_current_solar_data():
    """
    Get current solar activity data from NOAA SWPC
    
    Returns real-time measurements of:
    - Kp index (geomagnetic activity)
    - Sunspot number
    - Solar wind parameters
    
    This data updates approximately every 3 hours.
    """
    try:
        async with NOAAConnector() as noaa:
            # Fetch all current data
            kp_data = await noaa.get_kp_index_current()
            ssn_data = await noaa.get_sunspot_number_current()
            wind_data = await noaa.get_solar_wind_current()
            
            return SolarCurrentResponse(
                timestamp=datetime.utcnow().isoformat(),
                kp_index=kp_data['kp'],
                kp_status=kp_data['status'],
                sunspot_number=ssn_data['ssn'],
                smoothed_ssn=ssn_data['smoothed_ssn'],
                solar_cycle_phase=ssn_data['solar_cycle_phase'],
                solar_wind_speed=wind_data['speed'],
                proton_density=wind_data['density'],
                data_quality="good" if 'error' not in wind_data else "degraded"
            )
            
    except Exception as e:
        logger.error(f"Error fetching current solar data: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch solar data: {str(e)}"
        )


@router.get("/historical/kp", response_model=SolarHistoricalResponse)
async def get_historical_kp(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    include_classification: bool = Query(True, description="Include activity classification")
):
    """
    Get historical Kp index data
    
    The Kp index measures geomagnetic activity on a scale of 0-9.
    Data is typically available with ~3-hour resolution.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        include_classification: Whether to include activity level classification
    
    Returns:
        Historical Kp index time series
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Validate date range
        if end < start:
            raise HTTPException(
                status_code=400,
                detail="end_date must be after start_date"
            )
        
        if (end - start).days > 365:
            raise HTTPException(
                status_code=400,
                detail="Date range cannot exceed 365 days"
            )
        
        async with NOAAConnector() as noaa:
            df = await noaa.get_historical_kp(start, end)
            
            # Convert to list of dicts
            data = df.to_dict('records')
            
            # Add classification if requested
            if include_classification:
                for record in data:
                    record['status'] = NOAAConnector._classify_kp(record['kp'])
            
            return SolarHistoricalResponse(
                start_date=start_date,
                end_date=end_date,
                data_points=len(data),
                variables=['timestamp', 'kp'] + (['status'] if include_classification else []),
                data=data
            )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error fetching historical Kp data: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch historical data: {str(e)}"
        )


@router.get("/flares/recent", response_model=List[SolarFlareEvent])
async def get_recent_flares(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back")
):
    """
    Get recent solar flare events
    
    Solar flares are classified by X-ray intensity:
    - X-class: Major events that can trigger radio blackouts
    - M-class: Medium events
    - C-class: Minor events
    - B, A-class: Very minor events
    
    Args:
        days: Number of days to look back (1-30)
    
    Returns:
        List of solar flare events
    """
    try:
        async with NOAAConnector() as noaa:
            flares = await noaa.get_solar_flares_recent(days)
            
            return [
                SolarFlareEvent(
                    class_type=flare['class'],
                    intensity=flare['intensity'],
                    begin_time=flare['begin_time'],
                    peak_time=flare.get('peak_time'),
                    end_time=flare.get('end_time'),
                    location=flare.get('location')
                )
                for flare in flares
            ]
            
    except Exception as e:
        logger.error(f"Error fetching solar flares: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch flare data: {str(e)}"
        )


@router.get("/status")
async def get_solar_status():
    """
    Get human-readable solar activity status summary
    
    Provides a simplified summary of current space weather conditions
    suitable for display in dashboards or alerts.
    """
    try:
        async with NOAAConnector() as noaa:
            kp_data = await noaa.get_kp_index_current()
            ssn_data = await noaa.get_sunspot_number_current()
            
            # Generate status message
            if kp_data['kp'] < 4:
                geomag_msg = "Geomagnetic conditions are quiet"
                alert_level = "low"
            elif kp_data['kp'] < 6:
                geomag_msg = "Minor geomagnetic storm in progress"
                alert_level = "medium"
            else:
                geomag_msg = "Strong geomagnetic storm - auroras likely at high latitudes"
                alert_level = "high"
            
            # Solar cycle status
            if ssn_data['smoothed_ssn'] < 50:
                cycle_msg = "Solar minimum conditions"
            elif ssn_data['smoothed_ssn'] < 100:
                cycle_msg = "Solar activity increasing"
            else:
                cycle_msg = "Near solar maximum - increased activity expected"
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": kp_data['status'],
                "alert_level": alert_level,
                "geomagnetic_message": geomag_msg,
                "solar_cycle_message": cycle_msg,
                "kp_index": kp_data['kp'],
                "sunspot_number": ssn_data['ssn'],
                "data_freshness": "Current data from NOAA SWPC"
            }
            
    except Exception as e:
        logger.error(f"Error generating solar status: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to generate status summary"
        )


@router.get("/info")
async def get_solar_data_info():
    """
    Get information about solar data sources and metrics
    
    Provides metadata about what solar variables are monitored
    and how to interpret them.
    """
    return {
        "data_sources": {
            "primary": "NOAA Space Weather Prediction Center (SWPC)",
            "secondary": "NASA DONKI (future integration)",
            "update_frequency": "~3 hours for most metrics"
        },
        "metrics": {
            "kp_index": {
                "description": "Geomagnetic activity index (0-9)",
                "unit": "dimensionless",
                "interpretation": {
                    "0-2": "Quiet conditions",
                    "3-4": "Unsettled",
                    "5": "Minor storm",
                    "6": "Moderate storm",
                    "7": "Strong storm",
                    "8-9": "Severe to extreme storm"
                },
                "relevance": "May correlate with biological/psychological effects"
            },
            "sunspot_number": {
                "description": "Number of visible sunspots on solar disk",
                "unit": "count",
                "cycle": "~11 years",
                "relevance": "Indicates overall solar activity level"
            },
            "solar_wind": {
                "speed": "Velocity of solar wind (km/s), typical: 300-500",
                "density": "Proton density (p/cm³), typical: 5-10",
                "relevance": "High-speed streams can compress Earth's magnetosphere"
            }
        },
        "scientific_note": "Correlations between solar activity and terrestrial phenomena require rigorous statistical validation. See /docs for methodology.",
        "citation": "NOAA Space Weather Prediction Center. https://www.swpc.noaa.gov/"
    }
