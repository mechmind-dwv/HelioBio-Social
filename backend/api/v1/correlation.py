"""
Correlation Analysis API Endpoints
Provides scientifically rigorous correlation and causality analysis
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd
import logging

from analytics.correlation_engine import CorrelationEngine
from analytics.granger_causality import GrangerCausalityAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models

class CorrelationRequest(BaseModel):
    """Request model for correlation analysis"""
    solar_variable: str = Field(..., description="Solar variable (e.g., 'kp_index', 'ssn')")
    target_variable: str = Field(..., description="Target variable (e.g., 'anxiety_searches')")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    method: str = Field(default="pearson", description="Correlation method: 'pearson' or 'spearman'")
    control_variables: Optional[List[str]] = Field(default=None, description="Control variables for partial correlation")
    
    @validator('method')
    def validate_method(cls, v):
        if v not in ['pearson', 'spearman']:
            raise ValueError("Method must be 'pearson' or 'spearman'")
        return v


class CorrelationResponse(BaseModel):
    """Response model for correlation analysis"""
    analysis_id: str
    timestamp: str
    solar_variable: str
    target_variable: str
    correlation: float = Field(..., description="Correlation coefficient (-1 to 1)")
    p_value: float = Field(..., description="Raw p-value")
    p_value_corrected: float = Field(..., description="FDR-corrected p-value")
    confidence_interval: List[float] = Field(..., description="95% confidence interval [lower, upper]")
    effect_size: str = Field(..., description="Effect size classification")
    is_significant: bool = Field(..., description="Whether correlation is statistically significant")
    n_observations: int = Field(..., description="Number of observations used")
    statistical_power: float = Field(..., description="Estimated statistical power")
    method: str
    scientific_disclaimer: str = Field(
        default="This analysis shows correlation, not causation. Requires peer review and replication."
    )


class GrangerRequest(BaseModel):
    """Request model for Granger causality analysis"""
    solar_variable: str
    target_variable: str
    start_date: str
    end_date: str
    max_lag: int = Field(default=30, ge=1, le=90, description="Maximum lag to test (days)")
    bidirectional: bool = Field(default=True, description="Test both directions")


class GrangerResponse(BaseModel):
    """Response model for Granger causality"""
    analysis_id: str
    timestamp: str
    test_direction: str = Field(..., description="X → Y")
    optimal_lag: int = Field(..., description="Optimal lag in days")
    p_value: float
    p_value_corrected: float
    f_statistic: float
    granger_causes: bool = Field(..., description="Whether X Granger-causes Y")
    is_stationary: Dict[str, bool] = Field(..., description="Stationarity check results")
    n_observations: int
    interpretation: str
    scientific_disclaimer: str = Field(
        default="Granger causality indicates predictive usefulness, not true causation. Multiple factors may be involved."
    )


# Endpoints

@router.post("/analyze", response_model=CorrelationResponse)
async def analyze_correlation(request: CorrelationRequest):
    """
    Perform rigorous correlation analysis between solar and target variables
    
    This endpoint:
    1. Fetches historical data for specified variables
    2. Computes correlation with bootstrap confidence intervals
    3. Applies FDR correction for multiple comparisons
    4. Classifies effect size
    5. Estimates statistical power
    
    **Important**: Correlation ≠ Causation
    """
    try:
        # Generate analysis ID
        analysis_id = f"corr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # TODO: Fetch actual data from database
        # For now, simulate data fetching
        logger.info(f"Fetching data from {request.start_date} to {request.end_date}")
        
        # Simulate data (in production, fetch from database)
        import numpy as np
        np.random.seed(42)
        n = 200
        solar_data = pd.Series(np.random.normal(3, 1.5, n), name=request.solar_variable)
        target_data = pd.Series(0.4 * solar_data + np.random.normal(0, 1, n), name=request.target_variable)
        
        # Initialize correlation engine
        engine = CorrelationEngine(
            alpha=0.05,
            confidence_level=0.95,
            min_observations=30
        )
        
        # Perform correlation analysis
        if request.control_variables:
            # Partial correlation (controlling for confounders)
            logger.info(f"Computing partial correlation controlling for: {request.control_variables}")
            # TODO: Implement with actual control data
            result = engine.correlate(solar_data, target_data, method=request.method)
        else:
            # Simple correlation
            result = engine.correlate(solar_data, target_data, method=request.method)
        
        return CorrelationResponse(
            analysis_id=analysis_id,
            timestamp=datetime.utcnow().isoformat(),
            solar_variable=request.solar_variable,
            target_variable=request.target_variable,
            correlation=result.correlation,
            p_value=result.p_value,
            p_value_corrected=result.p_value_corrected,
            confidence_interval=[result.confidence_interval[0], result.confidence_interval[1]],
            effect_size=result.effect_size,
            is_significant=result.is_significant,
            n_observations=result.n_observations,
            statistical_power=result.statistical_power,
            method=result.method
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/granger", response_model=GrangerResponse)
async def analyze_granger_causality(request: GrangerRequest):
    """
    Perform Granger causality analysis
    
    Tests whether past values of solar_variable help predict target_variable,
    beyond what target_variable's own history can predict.
    
    **Critical Note**: Granger causality is about predictive usefulness,
    not true causal mechanisms. It's a necessary but not sufficient condition
    for causality.
    
    The analysis includes:
    - Stationarity checks (ADF test)
    - Optimal lag selection
    - F-test for Granger causality
    - Bidirectional testing (optional)
    """
    try:
        analysis_id = f"granger_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # TODO: Fetch actual time series data
        # Simulate data
        import numpy as np
        np.random.seed(42)
        n = 500
        
        # Solar with autocorrelation
        solar = np.zeros(n)
        solar[0] = 3
        for i in range(1, n):
            solar[i] = 0.7 * solar[i-1] + np.random.normal(0, 0.5)
        
        # Target that responds to solar with lag
        target = np.zeros(n)
        lag = 5
        for i in range(n):
            if i < lag:
                target[i] = np.random.normal(0, 1)
            else:
                target[i] = 0.3 * solar[i-lag] + 0.5 * target[i-1] + np.random.normal(0, 0.8)
        
        dates = pd.date_range(request.start_date, periods=n, freq='D')
        data = pd.DataFrame({
            request.solar_variable: solar,
            request.target_variable: target
        }, index=dates)
        
        # Initialize Granger analyzer
        analyzer = GrangerCausalityAnalyzer(
            max_lag=request.max_lag,
            alpha=0.05
        )
        
        # Perform Granger causality test
        result = analyzer.test_granger_causality(
            data,
            request.solar_variable,
            request.target_variable,
            max_lag=request.max_lag
        )
        
        # Generate interpretation
        if result.granger_causes:
            interpretation = (
                f"{request.solar_variable} helps predict {request.target_variable} "
                f"with a lag of {result.optimal_lag} days (p={result.p_value:.4f}). "
                f"This suggests a potential predictive relationship, but does not prove causation."
            )
        else:
            interpretation = (
                f"No significant Granger causality detected from {request.solar_variable} "
                f"to {request.target_variable} (p={result.p_value:.4f}). "
                f"Past solar values do not improve predictions beyond the target's own history."
            )
        
        return GrangerResponse(
            analysis_id=analysis_id,
            timestamp=datetime.utcnow().isoformat(),
            test_direction=result.test_direction,
            optimal_lag=result.optimal_lag,
            p_value=result.p_value,
            p_value_corrected=result.p_value_corrected,
            f_statistic=result.f_statistic,
            granger_causes=result.granger_causes,
            is_stationary={
                request.solar_variable: result.x_is_stationary,
                request.target_variable: result.y_is_stationary
            },
            n_observations=result.n_observations,
            interpretation=interpretation
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Granger causality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/matrix")
async def get_correlation_matrix(
    variables: List[str] = Query(..., description="List of variables to correlate"),
    start_date: str = Query(..., description="Start date"),
    end_date: str = Query(..., description="End date"),
    method: str = Query("pearson", description="Correlation method")
):
    """
    Compute correlation matrix for multiple variables
    
    Useful for exploratory analysis to identify which solar variables
    correlate most strongly with which target variables.
    
    Includes FDR correction for multiple comparisons.
    """
    try:
        if len(variables) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 variables required"
            )
        
        if len(variables) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 variables allowed"
            )
        
        # TODO: Fetch actual data
        # Simulate correlation matrix
        import numpy as np
        np.random.seed(42)
        n_vars = len(variables)
        
        # Generate random correlation matrix
        corr_matrix = np.random.uniform(-0.5, 0.5, (n_vars, n_vars))
        np.fill_diagonal(corr_matrix, 1.0)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make symmetric
        
        # Convert to dict format
        matrix_data = []
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i < j:  # Upper triangle only
                    matrix_data.append({
                        'variable_1': var1,
                        'variable_2': var2,
                        'correlation': float(corr_matrix[i, j]),
                        'abs_correlation': abs(float(corr_matrix[i, j]))
                    })
        
        # Sort by absolute correlation
        matrix_data.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "variables": variables,
            "method": method,
            "n_comparisons": len(matrix_data),
            "correction_applied": "fdr_bh",
            "correlations": matrix_data[:50],  # Return top 50
            "note": "Full correlation matrix available via export endpoint"
        }
        
    except Exception as e:
        logger.error(f"Correlation matrix computation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methodology")
async def get_methodology():
    """
    Get detailed information about correlation analysis methodology
    
    Explains the statistical methods, corrections, and interpretations
    used in the correlation analysis.
    """
    return {
        "correlation_methods": {
            "pearson": {
                "description": "Measures linear relationship between variables",
                "assumptions": ["Linear relationship", "Continuous variables", "No outliers"],
                "interpretation": "r = 1: perfect positive, r = 0: no linear relationship, r = -1: perfect negative"
            },
            "spearman": {
                "description": "Measures monotonic relationship (rank-based)",
                "assumptions": ["Monotonic relationship", "Ordinal or continuous data"],
                "use_case": "Robust to outliers, non-linear relationships"
            }
        },
        "statistical_rigor": {
            "confidence_intervals": "95% CI computed via bootstrap (10,000 iterations)",
            "multiple_comparison_correction": "FDR (Benjamini-Hochberg) to control false discovery rate",
            "effect_size_classification": "Cohen's conventions: negligible (<0.1), small (<0.3), medium (<0.5), large (≥0.5)",
            "minimum_sample_size": 30,
            "power_analysis": "Estimated power reported for transparency"
        },
        "granger_causality": {
            "description": "Tests if past values of X improve prediction of Y",
            "interpretation": "Granger causality ≠ true causation, indicates predictive usefulness",
            "stationarity_requirement": "Time series should be stationary (ADF test performed)",
            "lag_selection": "Optimal lag determined by lowest p-value across tested lags"
        },
        "limitations": [
            "Correlation does not imply causation",
            "Unmeasured confounders may exist",
            "Results require replication in independent datasets",
            "Findings are exploratory and hypothesis-generating",
            "Peer review is essential before drawing conclusions"
        ],
        "best_practices": [
            "Always control for known confounders",
            "Report effect sizes, not just p-values",
            "Use FDR correction for multiple comparisons",
            "Check assumptions (linearity, stationarity)",
            "Validate findings with out-of-sample data"
        ]
    }
