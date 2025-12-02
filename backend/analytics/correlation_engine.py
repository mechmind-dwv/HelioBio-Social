"""
Correlation Engine with Robust Statistical Controls
Implements scientifically rigorous correlation analysis with multiple comparison corrections
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, pearsonr
from statsmodels.stats.multitest import multipletests
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CorrelationResult:
    """Result container for correlation analysis"""
    correlation: float
    p_value: float
    p_value_corrected: float
    confidence_interval: Tuple[float, float]
    method: str
    n_observations: int
    effect_size: str
    statistical_power: float
    is_significant: bool
    correction_method: str


class CorrelationEngine:
    """
    Robust correlation analysis engine with scientific rigor
    """
    
    def __init__(
        self,
        alpha: float = 0.05,
        confidence_level: float = 0.95,
        min_observations: int = 30,
        correction_method: str = 'fdr_bh'
    ):
        """
        Initialize correlation engine
        
        Args:
            alpha: Significance level (default: 0.05)
            confidence_level: Confidence level for intervals (default: 0.95)
            min_observations: Minimum required observations (default: 30)
            correction_method: Multiple comparison correction ('bonferroni', 'fdr_bh', 'fdr_by')
        """
        self.alpha = alpha
        self.confidence_level = confidence_level
        self.min_observations = min_observations
        self.correction_method = correction_method
    
    def correlate(
        self,
        x: pd.Series,
        y: pd.Series,
        method: str = 'pearson',
        bootstrap_iterations: int = 10000
    ) -> CorrelationResult:
        """
        Compute correlation with robust statistical testing
        
        Args:
            x: First variable (e.g., solar activity)
            y: Second variable (e.g., mental health indicator)
            method: 'pearson' or 'spearman'
            bootstrap_iterations: Number of bootstrap samples for CI
        
        Returns:
            CorrelationResult object
        """
        # Clean data
        df = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(df) < self.min_observations:
            raise ValueError(
                f"Insufficient data: {len(df)} observations < {self.min_observations} required"
            )
        
        x_clean = df['x'].values
        y_clean = df['y'].values
        n = len(x_clean)
        
        # Compute correlation
        if method == 'pearson':
            corr, p_value = pearsonr(x_clean, y_clean)
        elif method == 'spearman':
            corr, p_value = spearmanr(x_clean, y_clean)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Bootstrap confidence interval
        ci = self._bootstrap_ci(x_clean, y_clean, method, bootstrap_iterations)
        
        # Effect size classification
        effect_size = self._classify_effect_size(corr)
        
        # Statistical power (simplified - assumes medium effect)
        power = self._estimate_power(n, corr, self.alpha)
        
        # Placeholder for correction (would be applied across multiple tests)
        p_value_corrected = p_value
        
        return CorrelationResult(
            correlation=corr,
            p_value=p_value,
            p_value_corrected=p_value_corrected,
            confidence_interval=ci,
            method=method,
            n_observations=n,
            effect_size=effect_size,
            statistical_power=power,
            is_significant=(p_value_corrected < self.alpha),
            correction_method=self.correction_method
        )
    
    def multiple_correlations(
        self,
        data: pd.DataFrame,
        x_cols: List[str],
        y_cols: List[str],
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Compute multiple correlations with FDR correction
        
        Args:
            data: DataFrame containing all variables
            x_cols: List of predictor variable names
            y_cols: List of outcome variable names
            method: Correlation method
        
        Returns:
            DataFrame with correlation results
        """
        results = []
        p_values = []
        
        # Compute all correlations
        for x_col in x_cols:
            for y_col in y_cols:
                try:
                    result = self.correlate(
                        data[x_col],
                        data[y_col],
                        method=method,
                        bootstrap_iterations=5000  # Reduced for speed
                    )
                    
                    results.append({
                        'x_variable': x_col,
                        'y_variable': y_col,
                        'correlation': result.correlation,
                        'p_value': result.p_value,
                        'n_observations': result.n_observations,
                        'effect_size': result.effect_size
                    })
                    
                    p_values.append(result.p_value)
                    
                except Exception as e:
                    logger.warning(f"Failed to correlate {x_col} vs {y_col}: {e}")
                    continue
        
        if not results:
            return pd.DataFrame()
        
        # Apply multiple comparison correction
        _, p_values_corrected, _, _ = multipletests(
            p_values,
            alpha=self.alpha,
            method=self.correction_method
        )
        
        # Add corrected p-values
        results_df = pd.DataFrame(results)
        results_df['p_value_corrected'] = p_values_corrected
        results_df['is_significant'] = results_df['p_value_corrected'] < self.alpha
        
        # Sort by significance
        results_df = results_df.sort_values('p_value_corrected')
        
        return results_df
    
    def partial_correlation(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        control_cols: List[str],
        method: str = 'pearson'
    ) -> CorrelationResult:
        """
        Compute partial correlation controlling for confounding variables
        
        Args:
            data: DataFrame with all variables
            x_col: Predictor variable
            y_col: Outcome variable
            control_cols: List of control variables
            method: Correlation method
        
        Returns:
            CorrelationResult for partial correlation
        """
        # Remove missing data
        cols = [x_col, y_col] + control_cols
        df = data[cols].dropna()
        
        if len(df) < self.min_observations:
            raise ValueError("Insufficient data after removing missing values")
        
        # Residualize x and y by control variables
        x_residuals = self._residualize(df[x_col], df[control_cols])
        y_residuals = self._residualize(df[y_col], df[control_cols])
        
        # Correlate residuals
        return self.correlate(
            pd.Series(x_residuals),
            pd.Series(y_residuals),
            method=method
        )
    
    def _bootstrap_ci(
        self,
        x: np.ndarray,
        y: np.ndarray,
        method: str,
        n_iterations: int
    ) -> Tuple[float, float]:
        """
        Compute bootstrap confidence interval for correlation
        
        Args:
            x, y: Data arrays
            method: Correlation method
            n_iterations: Number of bootstrap samples
        
        Returns:
            (lower_bound, upper_bound) tuple
        """
        n = len(x)
        bootstrap_corrs = []
        
        for _ in range(n_iterations):
            # Resample with replacement
            indices = np.random.choice(n, size=n, replace=True)
            x_boot = x[indices]
            y_boot = y[indices]
            
            # Compute correlation
            if method == 'pearson':
                corr, _ = pearsonr(x_boot, y_boot)
            else:
                corr, _ = spearmanr(x_boot, y_boot)
            
            bootstrap_corrs.append(corr)
        
        # Compute percentile confidence interval
        alpha_half = (1 - self.confidence_level) / 2
        lower = np.percentile(bootstrap_corrs, alpha_half * 100)
        upper = np.percentile(bootstrap_corrs, (1 - alpha_half) * 100)
        
        return (lower, upper)
    
    @staticmethod
    def _classify_effect_size(corr: float) -> str:
        """
        Classify effect size according to Cohen's conventions
        
        Args:
            corr: Correlation coefficient
        
        Returns:
            Effect size classification
        """
        abs_corr = abs(corr)
        
        if abs_corr < 0.1:
            return "negligible"
        elif abs_corr < 0.3:
            return "small"
        elif abs_corr < 0.5:
            return "medium"
        else:
            return "large"
    
    @staticmethod
    def _estimate_power(n: int, effect_size: float, alpha: float) -> float:
        """
        Estimate statistical power (simplified)
        
        Args:
            n: Sample size
            effect_size: Expected correlation
            alpha: Significance level
        
        Returns:
            Estimated power (0-1)
        """
        # Simplified power calculation using Fisher's z-transformation
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_transform = 0.5 * np.log((1 + effect_size) / (1 - effect_size))
        se = 1 / np.sqrt(n - 3)
        z_beta = z_transform / se - z_alpha
        power = stats.norm.cdf(z_beta)
        
        return max(0.0, min(1.0, power))
    
    @staticmethod
    def _residualize(y: pd.Series, X: pd.DataFrame) -> np.ndarray:
        """
        Compute residuals of y after regressing on X (for partial correlation)
        
        Args:
            y: Dependent variable
            X: Independent variables
        
        Returns:
            Residuals array
        """
        from sklearn.linear_model import LinearRegression
        
        model = LinearRegression()
        model.fit(X, y)
        predictions = model.predict(X)
        residuals = y.values - predictions
        
        return residuals


# Example usage
def example_usage():
    """Demonstrate correlation engine usage"""
    
    # Generate synthetic data
    np.random.seed(42)
    n = 100
    
    # Solar activity (e.g., Kp index)
    solar = np.random.normal(3, 1.5, n)
    
    # Mental health indicator with correlation to solar
    mental_health = 0.4 * solar + np.random.normal(0, 1, n)
    
    # Control variable (e.g., temperature)
    temperature = np.random.normal(20, 5, n)
    
    # Create DataFrame
    data = pd.DataFrame({
        'solar_activity': solar,
        'mental_health': mental_health,
        'temperature': temperature
    })
    
    # Initialize engine
    engine = CorrelationEngine(alpha=0.05, min_observations=30)
    
    # Simple correlation
    result = engine.correlate(
        data['solar_activity'],
        data['mental_health'],
        method='pearson'
    )
    
    print("=== Correlation Analysis ===")
    print(f"Correlation: {result.correlation:.3f}")
    print(f"p-value: {result.p_value:.4f}")
    print(f"95% CI: [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]")
    print(f"Effect size: {result.effect_size}")
    print(f"Statistical power: {result.statistical_power:.2f}")
    print(f"Significant: {result.is_significant}")
    
    # Partial correlation (controlling for temperature)
    partial_result = engine.partial_correlation(
        data,
        'solar_activity',
        'mental_health',
        ['temperature']
    )
    
    print("\n=== Partial Correlation (controlling temperature) ===")
    print(f"Partial correlation: {partial_result.correlation:.3f}")
    print(f"p-value: {partial_result.p_value:.4f}")


if __name__ == "__main__":
    example_usage()
