"""
🔮 ENDPOINTS AVANZADOS HELIOBIO-SOCIAL
Funcionalidades expandidas del sistema
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/advanced", tags=["advanced"])


@router.get("/historical-analysis")
async def historical_analysis(days: int = 30):
    """Análisis histórico de correlaciones"""
    # Simular datos históricos
    historical_data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        solar_activity = random.randint(10, 80)
        social_tension = random.uniform(0.1, 0.9)
        resonance = (solar_activity / 100) * social_tension

        historical_data.append(
            {
                "date": date.isoformat(),
                "solar_activity": solar_activity,
                "social_tension": social_tension,
                "resonance": resonance,
                "correlation_strength": (
                    "alta"
                    if resonance > 0.6
                    else "media" if resonance > 0.3 else "baja"
                ),
            }
        )

    return {
        "analysis_period": f"{days} días",
        "data_points": historical_data,
        "average_resonance": sum(d["resonance"] for d in historical_data)
        / len(historical_data),
        "max_correlation_day": max(historical_data, key=lambda x: x["resonance"]),
    }


@router.get("/predict-crispation")
async def predict_crispation(hours_ahead: int = 24):
    """Predecir niveles de crispación social"""
    # Simulación de predicción basada en patrones históricos
    current_resonance = random.uniform(0.2, 0.8)

    predictions = []
    for hour in range(0, hours_ahead + 1, 6):
        predicted_resonance = current_resonance + random.uniform(-0.2, 0.2)
        predictions.append(
            {
                "hours_from_now": hour,
                "predicted_resonance": max(0, min(1, predicted_resonance)),
                "crispation_risk": (
                    "ALTO"
                    if predicted_resonance > 0.7
                    else "MEDIO" if predicted_resonance > 0.5 else "BAJO"
                ),
                "confidence": random.uniform(0.6, 0.9),
            }
        )

    return {
        "prediction_horizon": f"{hours_ahead} horas",
        "current_resonance": current_resonance,
        "predictions": predictions,
        "recommendation": (
            "Monitorizar tendencias de conflicto"
            if any(p["crispation_risk"] == "ALTO" for p in predictions)
            else "Condiciones estables"
        ),
    }


@router.get("/chizhevsky-insights")
async def chizhevsky_insights():
    """Insights basados en la teoría de Chizhevsky"""
    insights = [
        {
            "period": "Máximo Solar (2024-2025)",
            "expected_impact": "Aumento de la actividad social y potencial de eventos históricos",
            "historical_precedent": "Revoluciones de 1848, Primavera Árabe 2011",
            "current_alignment": "85% alineado con patrones históricos",
        },
        {
            "period": "Mínimo Solar (2027-2028)",
            "expected_impact": "Periodos de estabilidad social y consolidación",
            "historical_precedent": "Periodos de paz y desarrollo tecnológico",
            "current_alignment": "Por monitorear",
        },
    ]

    return {
        "theory_basis": "Alexander Chizhevsky - Correlación entre ciclos solares y comportamiento humano",
        "current_cycle_phase": "Ascendente hacia máximo solar",
        "insights": insights,
        "research_references": [
            "Chizhevsky, A.L. (1924) 'Physical Factors of the Historical Process'",
            "NASA Solar Cycle Prediction Panel",
            "NOAA Space Weather Prediction Center",
        ],
    }
