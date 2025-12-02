import requests

# Obtener datos actuales
response = requests.get('http://localhost:8000/api/v1/solar/current')
solar_data = response.json()

# Análisis de correlación
response = requests.post('http://localhost:8000/api/v1/correlation/analyze', json={
    'solar_var': 'kp_index',
    'social_var': 'anxiety_trends',
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'control_vars': ['temperature', 'unemployment', 'holiday']
})

result = response.json()
print(f"Correlación: {result['correlation']:.3f}")
print(f"p-value (corregido): {result['p_value_corrected']:.4f}")
print(f"IC 95%: {result['confidence_interval']}")
