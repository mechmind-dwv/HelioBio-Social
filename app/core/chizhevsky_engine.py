"""
🧠 MOTOR CHIZHEVSKY - Núcleo de Conciencia HelioBio-Social
Implementación del legado de Alexander Chizhevsky para la era digital
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CosmicResonance:
    """Estructura para resonancias cósmicas detectadas"""

    solar_metric: str
    social_metric: str
    correlation_strength: float
    time_lag: timedelta
    confidence: float
    interpretation: str


class ChizhevskyEngine:
    """
    Motor principal que implementa las teorías de Chizhevsky
    para correlacionar actividad solar con comportamiento social digital
    """

    def __init__(self, solar_monitor, social_analyzer):
        self.solar_monitor = solar_monitor
        self.social_analyzer = social_analyzer
        self.status = "initializing"
        self.resonances: List[CosmicResonance] = []
        self.crispation_alerts: List[Dict] = []

        # Parámetros del modelo basados en investigación histórica
        self.solar_cycle_phase = "ascending"  # ascending, maximum, descending, minimum
        self.geomagnetic_sensitivity = 0.7
        self.collective_excitability_threshold = 0.65

        logger.info(
            "🚀 Motor Chizhevsky inicializado - Conectando dimensiones solares y sociales"
        )

    async def calculate_realtime_correlation(self) -> Dict[str, Any]:
        """Calcular correlación en tiempo real entre dimensiones"""
        try:
            # Obtener datos actuales
            solar_data = await self.solar_monitor.get_current_activity()
            social_data = await self.social_analyzer.get_current_analysis()

            # Calcular métricas de resonancia
            resonance_metrics = await self._compute_resonance_metrics(
                solar_data, social_data
            )

            # Interpretar según teoría de Chizhevsky
            interpretation = self._chizhevsky_interpretation(resonance_metrics)

            # Verificar alertas de crispación
            crispation_alert = self._check_crispation_alert(resonance_metrics)

            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "resonance_metrics": resonance_metrics,
                "chizhevsky_interpretation": interpretation,
                "crispation_alert": crispation_alert,
                "solar_cycle_phase": self.solar_cycle_phase,
                "collective_excitability": self._calculate_collective_excitability(
                    resonance_metrics
                ),
            }

            # Guardar resonancia significativa
            if resonance_metrics["overall_resonance"] > 0.6:
                resonance = CosmicResonance(
                    solar_metric="composite",
                    social_metric="composite",
                    correlation_strength=resonance_metrics["overall_resonance"],
                    time_lag=timedelta(hours=0),
                    confidence=0.85,
                    interpretation=interpretation,
                )
                self.resonances.append(resonance)

            self.status = "active"
            return result

        except Exception as e:
            logger.error(f"❌ Error en cálculo de correlación: {e}")
            self.status = "error"
            return {"error": str(e)}

    async def _compute_resonance_metrics(
        self, solar_data: Dict, social_data: Dict
    ) -> Dict[str, float]:
        """Computar métricas de resonancia entre dimensiones"""
        # Métricas solares clave
        solar_intensity = solar_data.get("sunspot_number", 0) / 300.0  # Normalizado
        solar_volatility = solar_data.get("flare_activity", 0) / 10.0  # Normalizado
        geomagnetic_activity = (
            solar_data.get("geomagnetic_storm", 0) / 9.0
        )  # Normalizado

        # Métricas sociales clave
        engagement_level = social_data.get("engagement_intensity", 0) / 100.0
        sentiment_polarity = abs(social_data.get("sentiment_polarity", 0))
        conflict_index = social_data.get("conflict_metric", 0)

        # Cálculo de resonancias específicas
        resonances = {
            "solar_social_engagement": self._pearson_similarity(
                [solar_intensity, solar_volatility],
                [engagement_level, sentiment_polarity],
            ),
            "geomagnetic_conflict": geomagnetic_activity * conflict_index,
            "solar_sentiment_volatility": solar_volatility * sentiment_polarity,
            "overall_resonance": (solar_intensity + solar_volatility)
            * (engagement_level + conflict_index)
            / 2,
        }

        return resonances

    def _chizhevsky_interpretation(self, resonance_metrics: Dict) -> str:
        """Interpretar resonancias según teoría de Chizhevsky"""
        overall = resonance_metrics.get("overall_resonance", 0)
        geomagnetic_conflict = resonance_metrics.get("geomagnetic_conflict", 0)

        if overall > 0.8 and geomagnetic_conflict > 0.7:
            return "ALTA RESONANCIA: Posible periodo de crispación social elevada - Máximo solar activando psique colectiva"
        elif overall > 0.6:
            return "RESONANCIA MODERADA: Actividad solar influyendo en tono emocional colectivo"
        elif overall > 0.4:
            return "RESONANCIA BAJA: Leve influencia solar en comportamiento social"
        else:
            return "RESONANCIA MÍNIMA: Influencia solar no detectable en corriente social actual"

    def _check_crispation_alert(self, resonance_metrics: Dict) -> Dict[str, Any]:
        """Verificar condiciones para alerta de crispación social"""
        conflict_level = resonance_metrics.get("geomagnetic_conflict", 0)
        overall_resonance = resonance_metrics.get("overall_resonance", 0)

        alert_threshold = self.collective_excitability_threshold

        if conflict_level > alert_threshold and overall_resonance > 0.7:
            alert = {
                "level": "HIGH",
                "message": "Condiciones de crispación social detectadas - Máxima resonancia solar-social",
                "confidence": 0.85,
                "recommendation": "Monitorear tendencias de conflicto en redes sociales",
                "chizhevsky_reference": "Periodos de máxima actividad solar correlacionan con tensión social histórica",
            }
            self.crispation_alerts.append(alert)
            return alert

        return {
            "level": "LOW",
            "message": "No se detectan condiciones críticas de crispación",
        }

    def _calculate_collective_excitability(self, resonance_metrics: Dict) -> float:
        """Calcular índice de excitabilidad colectiva basado en Chizhevsky"""
        base_excitability = resonance_metrics.get("overall_resonance", 0)

        # Modificar por fase del ciclo solar
        cycle_multipliers = {
            "ascending": 1.2,
            "maximum": 1.8,
            "descending": 1.1,
            "minimum": 0.7,
        }

        multiplier = cycle_multipliers.get(self.solar_cycle_phase, 1.0)
        return min(1.0, base_excitability * multiplier)

    def _pearson_similarity(self, list1: List[float], list2: List[float]) -> float:
        """Calcular similitud de Pearson entre dos listas"""
        if len(list1) != len(list2) or len(list1) == 0:
            return 0.0

        try:
            correlation = np.corrcoef(list1, list2)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
        except:
            return 0.0

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del motor Chizhevsky"""
        return {
            "status": self.status,
            "resonances_detected": len(self.resonances),
            "active_alerts": len(self.crispation_alerts),
            "solar_cycle_phase": self.solar_cycle_phase,
            "collective_excitability": getattr(self, "_last_excitability", 0),
        }
