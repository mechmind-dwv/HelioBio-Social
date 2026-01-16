"""
Motor de correlación científico para HelioBio-Social
Implementa métodos estadísticos robustos para correlacionar
actividad solar con indicadores de salud mental y comportamiento social
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests
import pywt
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class CorrelationResult:
    """Resultado estructurado de análisis de correlación"""
    method: str
    correlation_coefficient: float
    p_value: float
    confidence_interval: Tuple[float, float]
    n_observations: int
    lag: Optional[int] = None
    interpretation: Optional[str] = None
    effect_size: Optional[str] = None
    is_significant: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'method': self.method,
            'correlation': self.correlation_coefficient,
            'p_value': self.p_value,
            'confidence_interval': self.confidence_interval,
            'n_observations': self.n_observations,
            'lag': self.lag,
            'interpretation': self.interpretation,
            'effect_size': self.effect_size,
            'is_significant': self.is_significant
        }

class CorrelationEngine:
    """Motor principal de análisis de correlación"""
    
    def __init__(self, random_seed: int = 42):
        """Inicializar motor de correlación"""
        np.random.seed(random_seed)
        self.results_cache = {}
        
    def pearson_correlation(self, x: np.ndarray, y: np.ndarray, 
                           alpha: float = 0.05) -> CorrelationResult:
        """Correlación de Pearson con bootstrap para intervalos de confianza"""
        
        # Validar datos
        x_clean, y_clean = self._clean_and_align_data(x, y)
        
        if len(x_clean) < 10:
            raise ValueError("Insufficient data points for correlation analysis")
        
        # Calcular correlación de Pearson
        r, p_value = stats.pearsonr(x_clean, y_clean)
        
        # Bootstrap para intervalo de confianza
        n_bootstraps = 1000
        bootstrap_corrs = []
        
        for _ in range(n_bootstraps):
            indices = np.random.choice(len(x_clean), size=len(x_clean), replace=True)
            x_boot = x_clean[indices]
            y_boot = y_clean[indices]
            r_boot, _ = stats.pearsonr(x_boot, y_boot)
            bootstrap_corrs.append(r_boot)
        
        ci_lower = np.percentile(bootstrap_corrs, (alpha/2)*100)
        ci_upper = np.percentile(bootstrap_corrs, (1-alpha/2)*100)
        
        # Interpretación
        interpretation = self._interpret_correlation(r)
        effect_size = self._get_effect_size(r)
        
        result = CorrelationResult(
            method='pearson',
            correlation_coefficient=float(r),
            p_value=float(p_value),
            confidence_interval=(float(ci_lower), float(ci_upper)),
            n_observations=len(x_clean),
            interpretation=interpretation,
            effect_size=effect_size,
            is_significant=p_value < alpha
        )
        
        return result
    
    def spearman_correlation(self, x: np.ndarray, y: np.ndarray,
                           alpha: float = 0.05) -> CorrelationResult:
        """Correlación de Spearman (no paramétrica)"""
        
        x_clean, y_clean = self._clean_and_align_data(x, y)
        
        if len(x_clean) < 10:
            raise ValueError("Insufficient data points for correlation analysis")
        
        # Correlación de Spearman
        rho, p_value = stats.spearmanr(x_clean, y_clean)
        
        # Bootstrap para Spearman
        n_bootstraps = 1000
        bootstrap_rhos = []
        
        for _ in range(n_bootstraps):
            indices = np.random.choice(len(x_clean), size=len(x_clean), replace=True)
            x_boot = x_clean[indices]
            y_boot = y_clean[indices]
            rho_boot, _ = stats.spearmanr(x_boot, y_boot)
            bootstrap_rhos.append(rho_boot)
        
        ci_lower = np.percentile(bootstrap_rhos, (alpha/2)*100)
        ci_upper = np.percentile(bootstrap_rhos, (1-alpha/2)*100)
        
        interpretation = self._interpret_correlation(rho)
        effect_size = self._get_effect_size(rho)
        
        result = CorrelationResult(
            method='spearman',
            correlation_coefficient=float(rho),
            p_value=float(p_value),
            confidence_interval=(float(ci_lower), float(ci_upper)),
            n_observations=len(x_clean),
            interpretation=interpretation,
            effect_size=effect_size,
            is_significant=p_value < alpha
        )
        
        return result
    
    def granger_causality(self, x: np.ndarray, y: np.ndarray,
                         max_lag: int = 7,
                         test: str = 'ssr_chi2test',
                         alpha: float = 0.05) -> Dict[str, Any]:
        """
        Test de causalidad de Granger
        Determina si x ayuda a predecir y más allá de los valores pasados de y
        """
        
        x_clean, y_clean = self._clean_and_align_data(x, y)
        
        if len(x_clean) < max_lag * 5:
            raise ValueError(f"Need at least {max_lag*5} observations for Granger test")
        
        # Preparar datos para statsmodels
        data = pd.DataFrame({
            'y': y_clean,
            'x': x_clean
        })
        
        # Realizar test de Granger
        try:
            granger_test = grangercausalitytests(data[['y', 'x']], maxlag=max_lag, verbose=False)
            
            # Extraer mejores resultados
            best_lag = None
            best_p_value = 1.0
            best_f_statistic = 0.0
            all_results = []
            
            for lag in range(1, max_lag + 1):
                test_results = granger_test[lag][0][test]
                p_value = test_results[1]
                f_statistic = test_results[0]
                
                all_results.append({
                    'lag': lag,
                    'f_statistic': float(f_statistic),
                    'p_value': float(p_value),
                    'significant': p_value < alpha
                })
                
                if p_value < best_p_value:
                    best_p_value = p_value
                    best_f_statistic = f_statistic
                    best_lag = lag
            
            # Interpretación
            if best_p_value < alpha:
                causality = f"x Granger-causes y at lag {best_lag}"
                interpretation = f"Los valores pasados de x (hasta {best_lag} períodos) " \
                               f"ayudan significativamente a predecir y (p={best_p_value:.4f})"
            else:
                causality = "No Granger-causality detected"
                interpretation = "No hay evidencia de que x ayude a predecir y " \
                               "más allá de los valores pasados de y"
            
            return {
                'causality': causality,
                'best_lag': best_lag,
                'best_p_value': float(best_p_value),
                'best_f_statistic': float(best_f_statistic),
                'significant': best_p_value < alpha,
                'all_lags': all_results,
                'interpretation': interpretation,
                'test_used': test,
                'max_lag_tested': max_lag,
                'n_observations': len(x_clean)
            }
            
        except Exception as e:
            logger.error(f"Granger causality test failed: {e}")
            return {'error': str(e)}
    
    def wavelet_coherence(self, x: np.ndarray, y: np.ndarray,
                         scales: Optional[np.ndarray] = None,
                         wavelet: str = 'morl',
                         sampling_period: float = 1.0) -> Dict[str, Any]:
        """
        Análisis de coherencia wavelet
        Detecta correlaciones en el dominio tiempo-frecuencia
        """
        
        x_clean, y_clean = self._clean_and_align_data(x, y)
        
        if len(x_clean) < 128:
            raise ValueError("Need at least 128 observations for wavelet analysis")
        
        # Normalizar series
        x_norm = (x_clean - np.mean(x_clean)) / np.std(x_clean)
        y_norm = (y_clean - np.mean(y_clean)) / np.std(y_clean)
        
        # Definir escalas si no se proporcionan
        if scales is None:
            scales = np.arange(1, 65)
        
        # Calcular coeficientes wavelet para ambas series
        coeffs_x, freqs_x = pywt.cwt(x_norm, scales, wavelet, sampling_period)
        coeffs_y, freqs_y = pywt.cwt(y_norm, scales, wavelet, sampling_period)
        
        # Calcular coherencia wavelet
        cross_spectrum = coeffs_x * np.conj(coeffs_y)
        power_x = np.abs(coeffs_x) ** 2
        power_y = np.abs(coeffs_y) ** 2
        
        # Coherencia wavelet (magnitud al cuadrado)
        coherence = np.abs(cross_spectrum) ** 2 / (power_x * power_y)
        
        # Encontrar regiones de alta coherencia
        high_coherence_threshold = 0.7
        high_coherence_mask = coherence > high_coherence_threshold
        
        # Análisis de periodicidades
        avg_coherence_by_scale = np.mean(coherence, axis=1)
        dominant_scale_idx = np.argmax(avg_coherence_by_scale)
        dominant_period = scales[dominant_scale_idx]
        
        # Extraer fase para ver desfases
        phase = np.angle(cross_spectrum)
        
        return {
            'coherence_matrix': coherence.tolist(),
            'phase_matrix': phase.tolist(),
            'scales': scales.tolist(),
            'frequencies': freqs_x.tolist(),
            'dominant_period': float(dominant_period),
            'avg_coherence': float(np.mean(coherence)),
            'max_coherence': float(np.max(coherence)),
            'high_coherence_regions': np.where(high_coherence_mask),
            'interpretation': self._interpret_wavelet_results(coherence, dominant_period),
            'n_observations': len(x_clean)
        }
    
    def cross_correlation_analysis(self, x: np.ndarray, y: np.ndarray,
                                 max_lag: int = 30) -> Dict[str, Any]:
        """Análisis de correlación cruzada para detectar lags óptimos"""
        
        x_clean, y_clean = self._clean_and_align_data(x, y)
        
        # Calcular correlación cruzada
        cross_corr = np.correlate(x_clean - np.mean(x_clean), 
                                 y_clean - np.mean(y_clean), 
                                 mode='full')
        
        # Normalizar
        cross_corr = cross_corr / (np.std(x_clean) * np.std(y_clean) * len(x_clean))
        
        # Crear array de lags
        lags = np.arange(-len(x_clean) + 1, len(x_clean))
        
        # Encontrar lag con máxima correlación
        valid_lags = lags[abs(lags) <= max_lag]
        valid_corr = cross_corr[abs(lags) <= max_lag]
        
        if len(valid_corr) > 0:
            max_corr_idx = np.argmax(np.abs(valid_corr))
            optimal_lag = valid_lags[max_corr_idx]
            max_correlation = valid_corr[max_corr_idx]
            
            # Bootstrap para significancia
            n_bootstraps = 1000
            bootstrap_max_corrs = []
            
            for _ in range(n_bootstraps):
                y_shuffled = np.random.permutation(y_clean)
                corr_shuffled = np.correlate(x_clean - np.mean(x_clean),
                                           y_shuffled - np.mean(y_shuffled),
                                           mode='full')
                corr_shuffled = corr_shuffled / (np.std(x_clean) * np.std(y_shuffled) * len(x_clean))
                valid_corr_shuffled = corr_shuffled[abs(lags) <= max_lag]
                
                if len(valid_corr_shuffled) > 0:
                    bootstrap_max_corrs.append(np.max(np.abs(valid_corr_shuffled)))
            
            # Calcular p-value
            p_value = np.mean(np.array(bootstrap_max_corrs) >= abs(max_correlation))
            
            return {
                'optimal_lag': int(optimal_lag),
                'max_correlation': float(max_correlation),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'all_correlations': valid_corr.tolist(),
                'all_lags': valid_lags.tolist(),
                'interpretation': f"Máxima correlación en lag {optimal_lag}: {max_correlation:.3f}",
                'n_observations': len(x_clean)
            }
        else:
            return {'error': 'No valid lags found'}
    
    def time_lagged_correlation(self, x: pd.Series, y: pd.Series,
                               max_lag: int = 14) -> pd.DataFrame:
        """Correlación con diferentes lags temporales"""
        
        results = []
        
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                # x está adelantado respecto a y
                x_lagged = x.shift(-lag)
                y_aligned = y
                lag_desc = f"x leads by {-lag} days"
            elif lag > 0:
                # y está adelantado respecto a x
                x_lagged = x
                y_aligned = y.shift(lag)
                lag_desc = f"y leads by {lag} days"
            else:
                # Sin lag
                x_lagged = x
                y_aligned = y
                lag_desc = "no lag"
            
            # Alinear datos
            aligned_data = pd.DataFrame({
                'x': x_lagged,
                'y': y_aligned
            }).dropna()
            
            if len(aligned_data) > 10:
                r, p = stats.pearsonr(aligned_data['x'], aligned_data['y'])
                
                results.append({
                    'lag': lag,
                    'lag_description': lag_desc,
                    'correlation': r,
                    'p_value': p,
                    'n_observations': len(aligned_data),
                    'significant': p < 0.05
                })
        
        return pd.DataFrame(results)
    
    def multiple_correlation_analysis(self, solar_data: Dict[str, pd.Series],
                                     mental_health_data: Dict[str, pd.Series],
                                     methods: List[str] = None) -> Dict[str, Any]:
        """Análisis de correlación múltiple entre múltiples variables"""
        
        if methods is None:
            methods = ['pearson', 'spearman']
        
        results = {}
        
        for solar_var, solar_series in solar_data.items():
            for mental_var, mental_series in mental_health_data.items():
                # Alinear series temporales
                aligned = self._align_time_series(solar_series, mental_series)
                
                if len(aligned) < 10:
                    continue
                
                key = f"{solar_var}__{mental_var}"
                results[key] = {}
                
                # Aplicar múltiples métodos
                for method in methods:
                    try:
                        if method == 'pearson':
                            result = self.pearson_correlation(
                                aligned[solar_var].values,
                                aligned[mental_var].values
                            )
                        elif method == 'spearman':
                            result = self.spearman_correlation(
                                aligned[solar_var].values,
                                aligned[mental_var].values
                            )
                        elif method == 'granger':
                            result = self.granger_causality(
                                aligned[solar_var].values,
                                aligned[mental_var].values
                            )
                        else:
                            continue
                        
                        results[key][method] = result.to_dict() if hasattr(result, 'to_dict') else result
                        
                    except Exception as e:
                        logger.warning(f"Method {method} failed for {key}: {e}")
                        results[key][method] = {'error': str(e)}
        
        # Análisis agregado
        significant_correlations = []
        for key, methods_dict in results.items():
            for method, result in methods_dict.items():
                if isinstance(result, dict) and result.get('is_significant', False):
                    significant_correlations.append({
                        'variables': key,
                        'method': method,
                        'correlation': result.get('correlation_coefficient', result.get('correlation', 0)),
                        'p_value': result.get('p_value', 1)
                    })
        
        return {
            'individual_results': results,
            'significant_correlations': significant_correlations,
            'summary': {
                'total_analyses': len(results),
                'significant_findings': len(significant_correlations),
                'strongest_correlation': max(
                    [abs(c['correlation']) for c in significant_correlations] or [0]
                ),
                'most_significant': min(
                    [c['p_value'] for c in significant_correlations] or [1]
                )
            }
        }
    
    def _clean_and_align_data(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Limpiar y alinear datos para análisis"""
        # Convertir a arrays numpy
        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)
        
        # Eliminar NaN
        mask = ~(np.isnan(x_arr) | np.isnan(y_arr))
        x_clean = x_arr[mask]
        y_clean = y_arr[mask]
        
        # Verificar varianza
        if np.std(x_clean) == 0 or np.std(y_clean) == 0:
            raise ValueError("One or both series have zero variance")
        
        return x_clean, y_clean
    
    def _align_time_series(self, series1: pd.Series, series2: pd.Series) -> pd.DataFrame:
        """Alinear dos series temporales por fecha"""
        df1 = series1.reset_index()
        df2 = series2.reset_index()
        
        # Asumir que la columna de índice es la fecha
        date_col = df1.columns[0]
        
        merged = pd.merge(df1, df2, on=date_col, how='inner')
        merged = merged.set_index(date_col)
        
        return merged
    
    def _interpret_correlation(self, r: float) -> str:
        """Interpretar fuerza de la correlación"""
        abs_r = abs(r)
        
        if abs_r >= 0.7:
            return "Correlación muy fuerte"
        elif abs_r >= 0.5:
            return "Correlación fuerte"
        elif abs_r >= 0.3:
            return "Correlación moderada"
        elif abs_r >= 0.1:
            return "Correlación débil"
        else:
            return "Correlación muy débil o inexistente"
    
    def _get_effect_size(self, r: float) -> str:
        """Clasificar tamaño del efecto"""
        abs_r = abs(r)
        
        if abs_r >= 0.5:
            return "Grande"
        elif abs_r >= 0.3:
            return "Mediano"
        elif abs_r >= 0.1:
            return "Pequeño"
        else:
            return "Muy pequeño"
    
    def _interpret_wavelet_results(self, coherence: np.ndarray, dominant_period: float) -> str:
        """Interpretar resultados de análisis wavelet"""
        avg_coherence = np.mean(coherence)
        
        if avg_coherence > 0.7:
            coherence_str = "coherencia muy alta"
        elif avg_coherence > 0.5:
            coherence_str = "coherencia alta"
        elif avg_coherence > 0.3:
            coherence_str = "coherencia moderada"
        else:
            coherence_str = "coherencia baja"
        
        return f"Coherencia wavelet {coherence_str} con período dominante de {dominant_period:.1f} unidades de tiempo"

# Singleton global
correlation_engine = CorrelationEngine()
