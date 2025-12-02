from heliobio.analytics import CorrelationAnalyzer

# Cargar datos históricos
analyzer = CorrelationAnalyzer(
    start_date='2000-01-01',
    end_date='2024-12-31'
)

# Test de Granger con controles
result = analyzer.granger_causality(
    solar_var='kp_index',
    social_var='mental_health_searches',
    max_lag=30,
    control_vars=['temperature', 'day_of_week'],
    fdr_correction=True
)

if result.p_value_corrected < 0.05:
    print(f"Evidencia de relación predictiva (p={result.p_value_corrected:.4f})")
    print(f"Tamaño del efecto: {result.effect_size}")
else:
    print("No se encontró evidencia significativa")

# Generar reporte científico
report = analyzer.generate_report(
    format='pdf',
    include_robustness_checks=True,
    include_limitations=True
)
report.save('analysis_2024.pdf')heliobioanalytics
