"""
Granger Causality Analysis
Tests whether solar activity "Granger-causes" mental health indicators
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.stats.multitest import multipletests
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


@dataclass
class GrangerResult:
    """Container for Granger causality test results"""
    x_variable: str
    y_variable: str
    optimal_lag: int
    p_value: float
    p_value_corrected: float
    f_statistic: float
    granger_causes: bool
    x_is_stationary: bool
    y_is_stationary: bool
    n_observations: int
    test_direction: str


class GrangerCausalityAnalyzer:
    """
    Granger causality testing with proper stationarity checks
    
    Granger causality tests if past values of X help predict Y,
    beyond what Y's own past values can predict.
    
    IMPORTANT: Granger causality ≠ true causality
    It indicates predictive usefulness, not causal mechanism
    """
    
    def __init__(
        self,
        max_lag: int = 30,
        alpha: float = 0.05,
        adf_alpha: float = 0.05,
        correction_method: str = 'fdr_bh'
    ):
        """
        Initialize Granger causality analyzer
        
        Args:
            max_lag: Maximum lag to test (default: 30 days)
            alpha: Significance level for Granger test
            adf_alpha: Significance level for stationarity test (ADF)
            correction_method: Multiple comparison correction method
        """
        self.max_lag = max_lag
        self.alpha = alpha
        self.adf_alpha = adf_alpha
        self.correction_method = correction_method
    
    def test_granger_causality(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        max_lag: Optional[int] = None
    ) -> GrangerResult:
        """
        Test if X Granger-causes Y
        
        Args:
            data: DataFrame with time series data
            x_col: Predictor variable (e.g., 'kp_index')
            y_col: Outcome variable (e.g., 'anxiety_searches')
            max_lag: Maximum lag to test (defaults to self.max_lag)
        
        Returns:
            GrangerResult object
        """
        if max_lag is None:
            max_lag = self.max_lag
        
        # Prepare data
        df = data[[x_col, y_col]].dropna()
        
        if len(df) < max_lag + 50:  # Need sufficient data
            raise ValueError(
                f"Insufficient data: {len(df)} observations for max_lag={max_lag}"
            )
        
        # Check stationarity
        x_stationary = self._is_stationary(df[x_col])
        y_stationary = self._is_stationary(df[y_col])
        
        if not (x_stationary and y_stationary):
            logger.warning(
                f"Non-stationary series detected. "
                f"{x_col} stationary: {x_stationary}, "
                f"{y_col} stationary: {y_stationary}. "
                f"Consider differencing."
            )
        
        # Prepare data for Granger test (Y, X order required by statsmodels)
        test_data = df[[y_col, x_col]].values
        
        # Run Granger causality test
        try:
            results = grangercausalitytests(
                test_data,
                maxlag=max_lag,
                verbose=False
            )
            
            # Find optimal lag (lowest p-value)
            optimal_lag, p_value, f_stat = self._extract_best_result(results)
            
            return GrangerResult(
                x_variable=x_col,
                y_variable=y_col,
                optimal_lag=optimal_lag,
                p_value=p_value,
                p_value_corrected=p_value,  # Corrected later in batch testing
                f_statistic=f_stat,
                granger_causes=(p_value < self.alpha),
                x_is_stationary=x_stationary,
                y_is_stationary=y_stationary,
                n_observations=len(df),
                test_direction=f"{x_col} → {y_col}"
            )
            
        except Exception as e:
            logger.error(f"Granger test failed for {x_col} → {y_col}: {e}")
            raise
    
    def bidirectional_test(
        self,
        data: pd.DataFrame,
        var1: str,
        var2: str
    ) -> Tuple[GrangerResult, GrangerResult]:
        """
        Test Granger causality in both directions
        
        Args:
            data: DataFrame with time series
            var1: First variable
            var2: Second variable
        
        Returns:
            (var1 → var2 result, var2 → var1 result)
        """
        result_forward = self.test_granger_causality(data, var1, var2)
        result_backward = self.test_granger_causality(data, var2, var1)
        
        return result_forward, result_backward
    
    def multiple_granger_tests(
        self,
        data: pd.DataFrame,
        x_vars: List[str],
        y_vars: List[str]
    ) -> pd.DataFrame:
        """
        Test multiple Granger causality relationships with FDR correction
        
        Args:
            data: DataFrame with all variables
            x_vars: List of predictor variables
            y_vars: List of outcome variables
        
        Returns:
            DataFrame with all test results
        """
        results = []
        p_values = []
        
        for x_var in x_vars:
            for y_var in y_vars:
                if x_var == y_var:
                    continue
                
                try:
                    result = self.test_granger_causality(data, x_var, y_var)
                    
                    results.append({
                        'x_variable': result.x_variable,
                        'y_variable': result.y_variable,
                        'test_direction': result.test_direction,
                        'optimal_lag': result.optimal_lag,
                        'f_statistic': result.f_statistic,
                        'p_value': result.p_value,
                        'n_observations': result.n_observations,
                        'x_stationary': result.x_is_stationary,
                        'y_stationary': result.y_is_stationary
                    })
                    
                    p_values.append(result.p_value)
                    
                except Exception as e:
                    logger.warning(f"Granger test failed for {x_var} → {y_var}: {e}")
                    continue
        
        if not results:
            return pd.DataFrame()
        
        # Apply multiple comparison correction
        _, p_values_corrected, _, _ = multipletests(
            p_values,
            alpha=self.alpha,
            method=self.correction_method
        )
        
        results_df = pd.DataFrame(results)
        results_df['p_value_corrected'] = p_values_corrected
        results_df['granger_causes'] = results_df['p_value_corrected'] < self.alpha
        
        # Sort by significance
        results_df = results_df.sort_values('p_value_corrected')
        
        return results_df
    
    def _is_stationary(self, series: pd.Series) -> bool:
        """
        Test if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            series: Time series to test
        
        Returns:
            True if stationary (can reject null hypothesis of unit root)
        """
        try:
            result = adfuller(series.dropna(), autolag='AIC')
            p_value = result[1]
            return p_value < self.adf_alpha
        except Exception as e:
            logger.warning(f"ADF test failed: {e}")
            return False
    
    @staticmethod
    def _extract_best_result(
        granger_results: Dict
    ) -> Tuple[int, float, float]:
        """
        Extract optimal lag and statistics from Granger test results
        
        Args:
            granger_results: Output from grangercausalitytests
        
        Returns:
            (optimal_lag, p_value, f_statistic)
        """
        best_lag = 1
        best_p_value = 1.0
        best_f_stat = 0.0
        
        for lag, result in granger_results.items():
            # Get F-test result (ssr_ftest)
            f_test = result[0]['ssr_ftest']
            f_stat = f_test[0]
            p_value = f_test[1]
            
            if p_value < best_p_value:
                best_lag = lag
                best_p_value = p_value
                best_f_stat = f_stat
        
        return best_lag, best_p_value, best_f_stat
    
    @staticmethod
    def make_stationary(series: pd.Series, method: str = 'diff') -> pd.Series:
        """
        Transform non-stationary series to stationary
        
        Args:
            series: Non-stationary time series
            method: 'diff' (differencing) or 'log_diff' (log differencing)
        
        Returns:
            Stationary series
        """
        if method == 'diff':
            return series.diff().dropna()
        elif method == 'log_diff':
            return np.log(series).diff().dropna()
        else:
            raise ValueError(f"Unknown method: {method}")


# Example usage
def example_usage():
    """Demonstrate Granger causality analysis"""
    
    # Generate synthetic data
    np.random.seed(42)
    n = 500  # Need substantial data for Granger tests
    
    # Solar activity (with some autocorrelation)
    solar = np.zeros(n)
    solar[0] = np.random.normal(3, 1)
    for i in range(1, n):
        solar[i] = 0.7 * solar[i-1] + np.random.normal(0, 0.5)
    
    # Mental health indicator that responds to solar with lag
    lag = 5  # 5-day lag
    mental = np.zeros(n)
    for i in range(n):
        if i < lag:
            mental[i] = np.random.normal(0, 1)
        else:
            mental[i] = 0.3 * solar[i-lag] + 0.5 * mental[i-1] + np.random.normal(0, 0.8)
    
    # Create DataFrame with dates
    dates = pd.date_range('2020-01-01', periods=n, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'solar_activity': solar,
        'mental_health': mental
    }).set_index('date')
    
    # Initialize analyzer
    analyzer = GrangerCausalityAnalyzer(max_lag=15, alpha=0.05)
    
    # Test if solar Granger-causes mental health
    result = analyzer.test_granger_causality(
        data,
        'solar_activity',
        'mental_health'
    )
    
    print("=== Granger Causality Test ===")
    print(f"Direction: {result.test_direction}")
    print(f"Optimal lag: {result.optimal_lag} days")
    print(f"F-statistic: {result.f_statistic:.3f}")
    print(f"p-value: {result.p_value:.4f}")
    print(f"Granger causes: {result.granger_causes}")
    print(f"\nStationarity:")
    print(f"  Solar stationary: {result.x_is_stationary}")
    print(f"  Mental health stationary: {result.y_is_stationary}")
    
    # Bidirectional test
    print("\n=== Bidirectional Test ===")
    forward, backward = analyzer.bidirectional_test(
        data,
        'solar_activity',
        'mental_health'
    )
    
    print(f"Solar → Mental: p={forward.p_value:.4f}, causes={forward.granger_causes}")
    print(f"Mental → Solar: p={backward.p_value:.4f}, causes={backward.granger_causes}")
    
    if forward.granger_causes and not backward.granger_causes:
        print("\n✓ Evidence of unidirectional causality: Solar → Mental")
    elif backward.granger_causes and not forward.granger_causes:
        print("\n✓ Evidence of unidirectional causality: Mental → Solar")
    elif forward.granger_causes and backward.granger_causes:
        print("\n⚠ Evidence of bidirectional feedback")
    else:
        print("\n✗ No significant Granger causality detected")


if __name__ == "__main__":
    example_usage()
