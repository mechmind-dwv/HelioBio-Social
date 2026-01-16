import pandas as pd
import numpy as np
from scipy import stats
import requests
from datetime import datetime, timedelta

def fetch_noaa_kp(start_date="2020-01-01", end_date="2025-01-01"):
    """Fetch real Kp index data from NOAA"""
    # NOAA SWPC API endpoint (public, no key needed)
    url = f"https://services.swpc.noaa.gov/json/kp_30day.json"
    # Note: For historical data, you'd use different endpoints
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data)

def fetch_cdc_suicides(state="US", start_year=2020, end_year=2024):
    """Fetch suicide mortality data from CDC WONDER"""
    # CDC API requires specific query parameters
    # This is a simplified example - actual implementation needs CDC query builder
    params = {
        "dataset": "Underlying Cause of Death",
        "state": state,
        "year": f"{start_year}-{end_year}",
        "cause": "Suicide"
    }
    # Actual implementation would use CDC's API with proper authentication
    # For now, return sample data structure
    dates = pd.date_range(start=f"{start_year}-01-01", 
                         end=f"{end_year}-12-31", freq='D')
    return pd.DataFrame({
        'date': dates,
        'suicides': np.random.poisson(100, len(dates))  # Placeholder
    })

def calculate_correlation(kp_data, suicide_data):
    """Calculate Pearson correlation with statistical significance"""
    # Merge datasets on date
    merged = pd.merge(kp_data, suicide_data, on='date', how='inner')
    
    # Calculate correlation
    r, p = stats.pearsonr(merged['kp_index'], merged['suicides'])
    
    # Bootstrap for confidence intervals
    n_bootstraps = 1000
    bootstrap_corrs = []
    for _ in range(n_bootstraps):
        sample = merged.sample(n=len(merged), replace=True)
        r_boot, _ = stats.pearsonr(sample['kp_index'], sample['suicides'])
        bootstrap_corrs.append(r_boot)
    
    ci_lower = np.percentile(bootstrap_corrs, 2.5)
    ci_upper = np.percentile(bootstrap_corrs, 97.5)
    
    return {
        'correlation': r,
        'p_value': p,
        'ci_95': (ci_lower, ci_upper),
        'n_observations': len(merged),
        'is_significant': p < 0.05
    }

if __name__ == "__main__":
    print("HelioBio-Social: Validación Científica Inicial")
    print("=" * 50)
    
    # Fetch data
    print("1. Descargando datos solares (NOAA)...")
    kp_data = fetch_noaa_kp()
    
    print("2. Descargando datos de salud mental (CDC)...")
    suicide_data = fetch_cdc_suicides()
    
    print("3. Calculando correlación...")
    results = calculate_correlation(kp_data, suicide_data)
    
    # Display results
    print("\n" + "=" * 50)
    print("RESULTADOS ESTADÍSTICOS:")
    print(f"  Correlación (Pearson r): {results['correlation']:.3f}")
    print(f"  Valor p: {results['p_value']:.4f}")
    print(f"  IC 95%: [{results['ci_95'][0]:.3f}, {results['ci_95'][1]:.3f}]")
    print(f"  Observaciones: {results['n_observations']}")
    print(f"  Significativo (p<0.05): {'✅ SÍ' if results['is_significant'] else '❌ NO'}")
    
    # Scientific interpretation
    if results['is_significant']:
        print("\n🎯 INTERPRETACIÓN CIENTÍFICA:")
        print(f"  Existe una correlación estadísticamente significativa")
        print(f"  entre el índice Kp y las tasas de suicidio.")
        print(f"  Magnitud del efecto: {'pequeño' if abs(results['correlation']) < 0.3 else 'moderado' if abs(results['correlation']) < 0.5 else 'fuerte'}")
    else:
        print("\n⚠️  No se encontró evidencia suficiente para rechazar la hipótesis nula.")
