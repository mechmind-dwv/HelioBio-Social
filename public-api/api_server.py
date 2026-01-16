"""
Servidor API pública para investigadores científicos
Implementación completa de la especificación OpenAPI
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import logging
import asyncio
from contextlib import asynccontextmanager

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directorios de datos
DATA_DIR = Path("data/scientific")
PROCESSED_DIR = DATA_DIR / "processed"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la API"""
    logger.info("🚀 Iniciando HelioBio-Social Public API")
    
    # Cargar datos en memoria para rápido acceso
    app.state.datasets = {}
    
    try:
        # Cargar datasets procesados
        app.state.datasets['solar'] = pd.read_parquet(PROCESSED_DIR / "solar_processed.parquet")
        app.state.datasets['mental_health'] = pd.read_parquet(PROCESSED_DIR / "mental_health_processed.parquet")
        app.state.datasets['correlations'] = pd.read_parquet(PROCESSED_DIR / "precalculated_correlations.parquet")
        
        logger.info(f"✅ Datasets cargados:")
        logger.info(f"   - Solar: {len(app.state.datasets['solar'])} registros")
        logger.info(f"   - Salud mental: {len(app.state.datasets['mental_health'])} registros")
        logger.info(f"   - Correlaciones: {len(app.state.datasets['correlations'])} registros")
        
    except Exception as e:
        logger.error(f"❌ Error cargando datasets: {e}")
        app.state.datasets = {}
    
    yield
    
    # Limpieza
    logger.info("🛑 Apagando API pública")

# Crear aplicación
app = FastAPI(
    title="HelioBio-Social Scientific API",
    description="API pública para investigación en correlaciones solar-salud mental",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Customizar docs
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
def get_api_key(api_key: str = Query(None, alias="api_key")):
    """Validación simple de API key"""
    # En producción, usar base de datos de keys
    if api_key is None:
        # Permitir acceso básico sin key
        return "anonymous"
    
    valid_keys = ["scientific_researcher", "university_lab", "public_access"]
    if api_key in valid_keys:
        return api_key
    
    raise HTTPException(
        status_code=403,
        detail="API key inválida. Regístrese en https://heliobio.social/api-register"
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Agregar metadata adicional
    openapi_schema["info"]["x-logo"] = {
        "url": "https://heliobio.social/logo.png",
        "altText": "HelioBio-Social Logo"
    }
    
    openapi_schema["info"]["x-contact"] = {
        "email": "api@heliobio.social",
        "name": "HelioBio-Social Research Team",
        "url": "https://heliobio.social"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom docs UI
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentación",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://heliobio.social/favicon.ico"
    )

# Endpoints principales
@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "api": "HelioBio-Social Scientific API",
        "version": "1.0.0",
        "description": "API pública para investigación en correlaciones solar-salud mental",
        "documentation": "/docs",
        "datasets": {
            "solar": "/solar/historical",
            "mental_health": "/mental-health/indicators",
            "correlations": "/correlation/precalculated"
        },
        "citation": "HelioBio-Social Research Team. (2025). HelioBio-Social Scientific Dataset v1.0.",
        "license": "CC BY 4.0",
        "contact": "api@heliobio.social"
    }

@app.get("/health")
async def health_check():
    """Verificar estado de la API y datasets"""
    datasets_loaded = bool(app.state.datasets)
    dataset_status = {}
    
    if datasets_loaded:
        for name, df in app.state.datasets.items():
            dataset_status[name] = {
                "loaded": True,
                "records": len(df),
                "columns": len(df.columns),
                "date_range": {
                    "min": df['date'].min().isoformat() if 'date' in df.columns else None,
                    "max": df['date'].max().isoformat() if 'date' in df.columns else None
                }
            }
    else:
        dataset_status = {"error": "Datasets no cargados"}
    
    return {
        "status": "healthy" if datasets_loaded else "degraded",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "datasets": dataset_status,
        "memory_usage_mb": None  # Podría agregar monitoreo de memoria
    }

# Datos solares
@app.get("/solar/historical")
async def get_solar_historical(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    variables: Optional[List[str]] = Query(None, description="Variables específicas a incluir"),
    format: str = Query("json", description="Formato de respuesta (json, csv, parquet)"),
    api_key: str = Depends(get_api_key)
):
    """Obtener datos solares históricos"""
    
    if 'solar' not in app.state.datasets:
        raise HTTPException(status_code=503, detail="Dataset solar no disponible")
    
    df = app.state.datasets['solar'].copy()
    
    # Filtrar por fecha si se especifica
    if start_date:
        try:
            start_dt = pd.to_datetime(start_date)
            df = df[df['date'] >= start_dt]
        except:
            raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido")
    
    if end_date:
        try:
            end_dt = pd.to_datetime(end_date)
            df = df[df['date'] <= end_dt]
        except:
            raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido")
    
    # Seleccionar variables específicas
    if variables:
        available_cols = set(df.columns)
        requested_cols = set(['date'] + variables)
        
        # Verificar que todas las variables solicitadas existan
        invalid_vars = requested_cols - available_cols
        if invalid_vars:
            raise HTTPException(
                status_code=400,
                detail=f"Variables no disponibles: {list(invalid_vars)}"
            )
        
        df = df[list(requested_cols)]
    
    # Limitar resultados para usuarios anónimos
    if api_key == "anonymous" and len(df) > 1000:
        df = df.head(1000)
        warning = "Limitado a 1000 registros para acceso anónimo. Regístrese para acceso completo."
    else:
        warning = None
    
    # Formatear respuesta
    metadata = {
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "query_parameters": {
            "start_date": start_date,
            "end_date": end_date,
            "variables": variables,
            "format": format
        },
        "records_returned": len(df),
        "total_records_available": len(app.state.datasets['solar']),
        "warning": warning
    }
    
    # Retornar en formato solicitado
    if format == "csv":
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=solar_data_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    elif format == "parquet":
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        
        return StreamingResponse(
            parquet_buffer,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=solar_data_{datetime.now().strftime('%Y%m%d')}.parquet"
            }
        )
    
    else:  # JSON por defecto
        return {
            "metadata": metadata,
            "data": df.to_dict(orient="records")
        }

@app.get("/solar/realtime")
async def get_solar_realtime(api_key: str = Depends(get_api_key)):
    """Obtener datos solares en tiempo real (últimas 24 horas)"""
    
    # Simular datos en tiempo real para demo
    # En producción, conectar a API NOAA en tiempo real
    
    now = datetime.now()
    hours_24 = [now - timedelta(hours=i) for i in range(24)]
    
    # Generar datos sintéticos realistas
    data = []
    for timestamp in reversed(hours_24):
        # Variación diurna simulada
        hour = timestamp.hour
        base_kp = 2.0 + 0.5 * np.sin(2 * np.pi * hour / 24)
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "kp_index": round(base_kp + np.random.normal(0, 0.3), 1),
            "solar_wind_speed": round(400 + np.random.normal(0, 50), 1),
            "bz_component": round(np.random.normal(0, 3), 1),
            "proton_density": round(np.random.lognormal(1.5, 0.3), 1),
            "data_source": "NOAA SWPC (simulado para demo)",
            "update_frequency": "15 minutos"
        })
    
    return {
        "metadata": {
            "api_version": "1.0.0",
            "timestamp": now.isoformat(),
            "time_range": {
                "start": hours_24[0].isoformat(),
                "end": now.isoformat()
            },
            "note": "Datos de demostración. En producción: datos reales de NOAA."
        },
        "data": data
    }

# Datos de salud mental
@app.get("/mental-health/indicators")
async def get_mental_health_indicators(
    indicator: str = Query(..., description="Indicador de salud mental"),
    region: str = Query("GLOBAL", description="Región geográfica"),
    start_year: int = Query(2010, ge=2010, le=2025, description="Año de inicio"),
    end_year: int = Query(2025, ge=2010, le=2025, description="Año de fin"),
    api_key: str = Depends(get_api_key)
):
    """Obtener indicadores de salud mental"""
    
    if 'mental_health' not in app.state.datasets:
        raise HTTPException(status_code=503, detail="Dataset de salud mental no disponible")
    
    df = app.state.datasets['mental_health'].copy()
    
    # Validar indicador
    valid_indicators = [
        'depression_prevalence', 'anxiety_prevalence',
        'suicide_rate', 'bipolar_prevalence', 'schizophrenia_prevalence'
    ]
    
    if indicator not in valid_indicators:
        raise HTTPException(
            status_code=400,
            detail=f"Indicador inválido. Opciones: {valid_indicators}"
        )
    
    # Filtrar por región y años
    df = df[df['region'] == region]
    df = df[(df['date'].dt.year >= start_year) & (df['date'].dt.year <= end_year)]
    
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos para región '{region}' en el período {start_year}-{end_year}"
        )
    
    # Limitar para usuarios anónimos
    if api_key == "anonymous" and len(df) > 500:
        df = df.head(500)
        warning = "Limitado a 500 registros para acceso anónimo."
    else:
        warning = None
    
    # Calcular estadísticas descriptivas
    if indicator in df.columns:
        values = df[indicator].dropna()
        stats = {
            "mean": float(values.mean()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "n": len(values)
        }
    else:
        stats = None
    
    return {
        "metadata": {
            "api_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "indicator": indicator,
            "region": region,
            "years": f"{start_year}-{end_year}",
            "data_source": "WHO Global Health Observatory, CDC WONDER",
            "warning": warning
        },
        "statistics": stats,
        "data": df[['date', indicator, 'region', 'data_source']].to_dict(orient="records")
    }

# Correlaciones
@app.get("/correlation/precalculated")
async def get_precalculated_correlations(
    solar_variable: Optional[str] = Query(None, description="Variable solar"),
    mental_variable: Optional[str] = Query(None, description="Variable de salud mental"),
    window_months: Optional[int] = Query(None, description="Ventana temporal en meses"),
    api_key: str = Depends(get_api_key)
):
    """Obtener correlaciones pre-calculadas"""
    
    if 'correlations' not in app.state.datasets:
        raise HTTPException(status_code=503, detail="Dataset de correlaciones no disponible")
    
    df = app.state.datasets['correlations'].copy()
    
    # Aplicar filtros
    if solar_variable:
        df = df[df['solar_variable'] == solar_variable]
    
    if mental_variable:
        df = df[df['mental_variable'] == mental_variable]
    
    if window_months:
        df = df[df['window_months'] == window_months]
    
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron correlaciones con los filtros especificados"
        )
    
    # Agregar estadísticas
    if 'correlation' in df.columns:
        corr_values = df['correlation'].dropna()
        stats = {
            "mean_correlation": float(corr_values.mean()),
            "std_correlation": float(corr_values.std()),
            "min_correlation": float(corr_values.min()),
            "max_correlation": float(corr_values.max()),
            "significant_positive": int((corr_values > 0.3).sum()),
            "significant_negative": int((corr_values < -0.3).sum()),
            "total_calculations": len(corr_values)
        }
    else:
        stats = None
    
    return {
        "metadata": {
            "api_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "filters_applied": {
                "solar_variable": solar_variable,
                "mental_variable": mental_variable,
                "window_months": window_months
            },
            "total_results": len(df)
        },
        "statistics": stats,
        "data": df.to_dict(orient="records")
    }

@app.post("/correlation/calculate")
async def calculate_correlation(
    request: Dict[str, Any] = Body(...),
    api_key: str = Depends(get_api_key)
):
    """Calcular correlación personalizada"""
    
    # Validar request
    required_fields = ['solar_variable', 'mental_variable', 'method']
    missing_fields = [f for f in required_fields if f not in request]
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Campos requeridos faltantes: {missing_fields}"
        )
    
    solar_var = request['solar_variable']
    mental_var = request['mental_variable']
    method = request['method']
    
    # Validar métodos
    valid_methods = ['pearson', 'spearman', 'granger', 'wavelet']
    if method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Método inválido. Opciones: {valid_methods}"
        )
    
    # Obtener datos
    if 'solar' not in app.state.datasets or 'mental_health' not in app.state.datasets:
        raise HTTPException(status_code=503, detail="Datasets no disponibles")
    
    solar_df = app.state.datasets['solar'].copy()
    mental_df = app.state.datasets['mental_health'].copy()
    
    # Filtrar por región si se especifica
    region = request.get('region', 'GLOBAL')
    mental_df = mental_df[mental_df['region'] == region]
    
    # Filtrar por fecha
    start_date = request.get('start_date', '2010-01-01')
    end_date = request.get('end_date', '2025-12-31')
    
    try:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        solar_df = solar_df[(solar_df['date'] >= start_dt) & (solar_df['date'] <= end_dt)]
        mental_df = mental_df[(mental_df['date'] >= start_dt) & (mental_df['date'] <= end_dt)]
    except:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    # Verificar que las variables existan
    if solar_var not in solar_df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Variable solar '{solar_var}' no encontrada"
        )
    
    if mental_var not in mental_df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Variable de salud mental '{mental_var}' no encontrada"
        )
    
    # Merge por fecha
    merged = pd.merge(
        solar_df[['date', solar_var]],
        mental_df[['date', mental_var]],
        on='date',
        how='inner'
    ).dropna()
    
    if len(merged) < 10:
        raise HTTPException(
            status_code=400,
            detail="Datos insuficientes para análisis (mínimo 10 observaciones)"
        )
    
    # Extraer series
    x = merged[solar_var].values
    y = merged[mental_var].values
    
    # Calcular correlación según método
    from scipy import stats
    import statsmodels.api as sm
    
    result = {
        "method": method,
        "solar_variable": solar_var,
        "mental_variable": mental_var,
        "region": region,
        "time_period": f"{start_date} to {end_date}",
        "n_observations": len(merged),
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if method == 'pearson':
            r, p = stats.pearsonr(x, y)
            result.update({
                "correlation_coefficient": float(r),
                "p_value": float(p),
                "significant": p < 0.05,
                "interpretation": self._interpret_correlation(r)
            })
        
        elif method == 'spearman':
            rho, p = stats.spearmanr(x, y)
            result.update({
                "correlation_coefficient": float(rho),
                "p_value": float(p),
                "significant": p < 0.05,
                "interpretation": self._interpret_correlation(rho)
            })
        
        elif method == 'granger':
            # Test de Granger simplificado
            from statsmodels.tsa.stattools import grangercausalitytests
            
            data = pd.DataFrame({'x': x, 'y': y})
            max_lag = min(7, len(data) // 5)  # Lag máximo basado en tamaño de muestra
            
            if max_lag < 1:
                raise ValueError("Datos insuficientes para test de Granger")
            
            test_result = grangercausalitytests(data, maxlag=max_lag, verbose=False)
            
            # Encontrar mejor lag
            best_lag = None
            best_p = 1.0
            
            for lag in range(1, max_lag + 1):
                p_value = test_result[lag][0]['ssr_chi2test'][1]
                if p_value < best_p:
                    best_p = p_value
                    best_lag = lag
            
            result.update({
                "optimal_lag": best_lag,
                "p_value": float(best_p),
                "significant": best_p < 0.05,
                "causality": "x Granger-causes y" if best_p < 0.05 else "No Granger-causality detected",
                "interpretation": self._interpret_granger(best_p, best_lag)
            })
        
        elif method == 'wavelet':
            # Análisis wavelet simplificado
            import pywt
            
            # Coherencia wavelet básica
            scales = np.arange(1, 65)
            coef_x, _ = pywt.cwt(x, scales, 'morl')
            coef_y, _ = pywt.cwt(y, scales, 'morl')
            
            # Calcular coherencia
            coherencia = np.abs(np.mean(coef_x * np.conj(coef_y), axis=1))
            dominant_scale = scales[np.argmax(coherencia)]
            
            result.update({
                "dominant_period": int(dominant_scale),
                "max_coherence": float(np.max(coherencia)),
                "mean_coherence": float(np.mean(coherencia)),
                "interpretation": f"Coherencia máxima en período {dominant_scale}"
            })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en cálculo de {method}: {str(e)}"
        )
    
    return result

def _interpret_correlation(self, r: float) -> str:
    """Interpretar fuerza de correlación"""
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

def _interpret_granger(self, p: float, lag: int) -> str:
    """Interpretar test de Granger"""
    if p < 0.05:
        return f"La actividad solar predice variaciones en salud mental con {lag} días de antelación (p={p:.4f})"
    else:
        return f"No hay evidencia de que la actividad solar prediga variaciones en salud mental (p={p:.4f})"

# Metadata y documentación
@app.get("/metadata/dataset")
async def get_dataset_metadata():
    """Obtener metadatos completos del dataset"""
    
    metadata_path = DATA_DIR / "metadata" / "dataset_metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    else:
        # Metadatos por defecto
        metadata = {
            "title": "HelioBio-Social Scientific Dataset",
            "version": "1.0.0",
            "publication_date": "2025-01-01",
            "license": "CC BY 4.0",
            "doi": "10.5281/zenodo.xxxxxxx",
            "creators": [
                {
                    "name": "HelioBio-Social Research Team",
                    "affiliation": "Open Science Collective"
                }
            ],
            "keywords": [
                "heliobiology", "solar activity", "mental health",
                "epidemiology", "time series analysis"
            ],
            "temporal_coverage": {
                "start_date": "2010-01-01",
                "end_date": "2025-12-31"
            },
            "spatial_coverage": ["Global", "Europe", "Americas", "Africa", "Asia Pacific"],
            "variables": 45,
            "size_gb": 0.5,
            "update_frequency": "Annual",
            "citation": "HelioBio-Social Research Team. (2025). HelioBio-Social Scientific Dataset v1.0.",
            "access_restrictions": "Open access for scientific research"
        }
    
    return metadata

@app.get("/documentation/codebook")
async def get_codebook():
    """Obtener libro de códigos completo"""
    
    codebook_path = DATA_DIR / "documentation" / "DATA_DICTIONARY.md"
    
    if codebook_path.exists():
        with open(codebook_path, 'r') as f:
            content = f.read()
        
        return {
            "format": "markdown",
            "content": content
        }
    else:
        # Codebook básico
        codebook = {
            "solar_variables": {
                "kp_index": {
                    "description": "Índice Kp geomagnético (0-9)",
                    "unit": "unitless",
                    "source": "NOAA SWPC",
                    "range": "0-9",
                    "notes": "Valores ≥5 indican tormenta geomagnética"
                },
                "sunspot_number": {
                    "description": "Número de manchas solares",
                    "unit": "count",
                    "source": "NOAA NCEI",
                    "range": "0-300",
                    "notes": "Indicador de actividad solar general"
                }
            },
            "mental_health_variables": {
                "depression_prevalence": {
                    "description": "Prevalencia de depresión mayor",
                    "unit": "percentage",
                    "source": "WHO GHO",
                    "range": "0-20%",
                    "notes": "Estimaciones anuales por país"
                },
                "suicide_rate": {
                    "description": "Tasa de suicidio",
                    "unit": "per 100,000 population",
                    "source": "WHO, CDC",
                    "range": "0-50",
                    "notes": "Ajustada por edad"
                }
            }
        }
        
        return codebook

# Herramientas científicas
@app.post("/tools/statistical-test")
async def run_statistical_test(
    request: Dict[str, Any] = Body(...),
    api_key: str = Depends(get_api_key)
):
    """Ejecutar test estadístico sobre datos proporcionados"""
    
    from scipy import stats
    
    test_type = request.get('test', 't_test')
    data1 = request.get('data1', [])
    data2 = request.get('data2', [])
    
    if not data1:
        raise HTTPException(status_code=400, detail="Se requieren datos (data1)")
    
    result = {
        "test": test_type,
        "timestamp": datetime.now().isoformat(),
        "n_data1": len(data1),
        "n_data2": len(data2) if data2 else 0
    }
    
    try:
        if test_type == 't_test':
            if not data2:
                # One-sample t-test
                stat, p = stats.ttest_1samp(data1, 0)
                result.update({
                    "statistic": float(stat),
                    "p_value": float(p),
                    "test": "one_sample_t_test"
                })
            else:
                # Two-sample t-test
                stat, p = stats.ttest_ind(data1, data2)
                result.update({
                    "statistic": float(stat),
                    "p_value": float(p),
                    "test": "two_sample_t_test"
                })
        
        elif test_type == 'mann_whitney':
            if not data2:
                raise HTTPException(
                    status_code=400,
                    detail="Test Mann-Whitney requiere dos grupos de datos"
                )
            
            stat, p = stats.mannwhitneyu(data1, data2)
            result.update({
                "statistic": float(stat),
                "p_value": float(p)
            })
        
        elif test_type == 'chi_square':
            # Para chi-square, esperamos tablas de contingencia
            observed = request.get('observed_table')
            if not observed:
                raise HTTPException(
                    status_code=400,
                    detail="Test chi-cuadrado requiere tabla observada"
                )
            
            stat, p, dof, expected = stats.chi2_contingency(observed)
            result.update({
                "statistic": float(stat),
                "p_value": float(p),
                "degrees_of_freedom": int(dof)
            })
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Test no soportado: {test_type}"
            )
        
        # Interpretación
        result['significant'] = result.get('p_value', 1) < 0.05
        result['interpretation'] = self._interpret_statistical_test(result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en test estadístico: {str(e)}"
        )
    
    return result

def _interpret_statistical_test(self, result: Dict) -> str:
    """Interpretar resultado de test estadístico"""
    p = result.get('p_value', 1)
    
    if p < 0.001:
        sig = "altamente significativo"
    elif p < 0.01:
        sig = "muy significativo"
    elif p < 0.05:
        sig = "significativo"
    else:
        sig = "no significativo"
    
    test_name = result.get('test', 'statistical test')
    
    return f"El resultado del {test_name} es {sig} (p={p:.4f})"

# Middleware para logging y rate limiting
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para logging de requests"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    # Agregar headers informativos
    response.headers["X-API-Version"] = "1.0.0"
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-Correlation-ID"] = f"req_{start_time.timestamp()}"
    
    return response

# Ejecutar servidor
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
