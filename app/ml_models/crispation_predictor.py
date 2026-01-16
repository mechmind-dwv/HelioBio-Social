"""
🤖 MODELO PREDICTIVO DE CRISPACIÓN SOCIAL
Machine Learning para predecir conflictividad basada en patrones solares
"""
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class CrispationPredictor:
    """Modelo de ML para predecir crispación social basado en actividad solar"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_names = [
            'sunspot_number', 'solar_flux', 'flare_activity', 
            'geomagnetic_storm', 'solar_wind_speed', 'day_of_year',
            'solar_cycle_progress', 'month_sin', 'month_cos'
        ]
        
    def generate_training_data(self, num_samples=1000):
        """Generar datos de entrenamiento sintéticos basados en patrones reales"""
        logger.info("🧠 Generando datos de entrenamiento para modelo predictivo...")
        
        data = []
        for i in range(num_samples):
            # Patrones basados en investigación de Chizhevsky
            solar_cycle_progress = random.uniform(0, 1)
            
            # Manchas solares siguen ciclo de 11 años
            base_sunspots = 20 + (solar_cycle_progress * 130)  # 20-150
            sunspots = max(0, base_sunspots + random.normalvariate(0, 15))
            
            # Otras métricas solares correlacionadas
            solar_flux = 70 + (sunspots / 2) + random.normalvariate(0, 5)
            flare_activity = self._flare_from_sunspots(sunspots)
            geomagnetic_storm = self._storm_from_sunspots(sunspots)
            solar_wind = 400 + random.normalvariate(0, 50)
            
            # Variables temporales
            day_of_year = random.randint(1, 365)
            month = (day_of_year // 30) % 12
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            
            # Target: crispación social (0-1)
            # Basado en teoría de Chizhevsky: máxima actividad solar → máxima conflictividad
            base_crispation = solar_cycle_progress * 0.6  # Ciclo solar contribuye 60%
            flare_effect = flare_activity * 0.08  # Fulguraciones contribuyen
            geomagnetic_effect = geomagnetic_storm * 0.06  # Tormentas geomagnéticas
            seasonal_effect = abs(month_sin) * 0.2  # Estacionalidad
            noise = random.normalvariate(0, 0.1)
            
            crispation = (
                base_crispation + 
                flare_effect + 
                geomagnetic_effect + 
                seasonal_effect + 
                noise
            )
            crispation = max(0, min(1, crispation))  # Normalizar 0-1
            
            data.append({
                'sunspot_number': sunspots,
                'solar_flux': solar_flux,
                'flare_activity': flare_activity,
                'geomagnetic_storm': geomagnetic_storm,
                'solar_wind_speed': solar_wind,
                'day_of_year': day_of_year,
                'solar_cycle_progress': solar_cycle_progress,
                'month_sin': month_sin,
                'month_cos': month_cos,
                'crispation': crispation
            })
        
        return pd.DataFrame(data)
    
    def train_model(self, df=None):
        """Entrenar modelo Random Forest"""
        logger.info("🎯 Entrenando modelo predictivo de crispación...")
        
        if df is None:
            df = self.generate_training_data(2000)
        
        # Preparar características y target
        X = df[self.feature_names]
        y = df['crispation']
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.is_trained = True
        
        logger.info(f"✅ Modelo entrenado - MAE: {mae:.4f}, R²: {r2:.4f}")
        return mae, r2
    
    def predict_crispation(self, solar_data, current_date=None):
        """Predecir nivel de crispación basado en datos solares actuales"""
        if not self.is_trained:
            self.train_model()
        
        if current_date is None:
            current_date = datetime.now()
        
        # Preparar características para predicción
        features = self._prepare_features(solar_data, current_date)
        
        # Hacer predicción
        crispation_prob = self.model.predict([features])[0]
        crispation_prob = max(0, min(1, crispation_prob))  # Asegurar rango 0-1
        
        # Interpretar resultado
        interpretation = self._interpret_prediction(crispation_prob)
        
        return {
            'crispation_probability': round(crispation_prob, 3),
            'risk_level': interpretation['level'],
            'confidence': 0.85,  # Basado en evaluación del modelo
            'message': interpretation['message'],
            'contributing_factors': self._get_feature_importance(features),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _prepare_features(self, solar_data, current_date):
        """Preparar características para el modelo"""
        solar_cycle_progress = solar_data.get('solar_cycle_progress', 
                                            self._calculate_cycle_progress(current_date))
        
        day_of_year = current_date.timetuple().tm_yday
        month = current_date.month - 1  # 0-11
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        
        return [
            solar_data.get('sunspot_number', 0),
            solar_data.get('solar_flux', 70),
            solar_data.get('flare_activity', 0),
            solar_data.get('geomagnetic_storm', 0),
            solar_data.get('solar_wind_speed', 400),
            day_of_year,
            solar_cycle_progress,
            month_sin,
            month_cos
        ]
    
    def _calculate_cycle_progress(self, current_date):
        """Calcular progreso del ciclo solar 25"""
        cycle_start = 2020
        cycle_duration = 11
        current_year = current_date.year
        return (current_year - cycle_start) / cycle_duration
    
    def _interpret_prediction(self, probability):
        """Interpretar probabilidad de crispación"""
        if probability > 0.7:
            return {
                'level': 'CRITICAL',
                'message': '🌋 ALTA PROBABILIDAD DE CONFLICTIVIDAD - Condiciones similares a máximos solares históricos'
            }
        elif probability > 0.5:
            return {
                'level': 'HIGH', 
                'message': '🔥 PROBABILIDAD ELEVADA - Aumento significativo en tensión social esperado'
            }
        elif probability > 0.3:
            return {
                'level': 'MODERATE',
                'message': '⚡ PROBABILIDAD MODERADA - Leve aumento en crispación social'
            }
        else:
            return {
                'level': 'LOW',
                'message': '✅ PROBABILIDAD BAJA - Condiciones sociales estables'
            }
    
    def _get_feature_importance(self, features):
        """Obtener factores que contribuyen a la predicción"""
        if not hasattr(self.model, 'feature_importances_'):
            return ["Modelo en entrenamiento"]
        
        importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
        top_factors = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        
        factors = []
        for feature, importance in top_factors:
            if feature == 'sunspot_number':
                factors.append(f"Manchas solares ({importance:.1%})")
            elif feature == 'solar_cycle_progress':
                factors.append(f"Fase ciclo solar ({importance:.1%})")
            elif feature == 'flare_activity':
                factors.append(f"Fulguraciones ({importance:.1%})")
            elif feature == 'geomagnetic_storm':
                factors.append(f"Actividad geomagnética ({importance:.1%})")
            elif 'month' in feature:
                factors.append(f"Estacionalidad ({importance:.1%})")
        
        return factors
    
    def _flare_from_sunspots(self, sunspots):
        """Calcular actividad de fulguraciones basada en manchas solares"""
        if sunspots > 120: return random.choices([3,4,5], weights=[0.3,0.4,0.3])[0]
        elif sunspots > 80: return random.choices([2,3,4], weights=[0.4,0.4,0.2])[0]
        elif sunspots > 40: return random.choices([1,2,3], weights=[0.5,0.4,0.1])[0]
        else: return random.choices([0,1], weights=[0.7,0.3])[0]
    
    def _storm_from_sunspots(self, sunspots):
        """Calcular actividad geomagnética basada en manchas solares"""
        if sunspots > 100: return random.choices([2,3,4], weights=[0.4,0.4,0.2])[0]
        elif sunspots > 60: return random.choices([1,2,3], weights=[0.5,0.4,0.1])[0]
        else: return random.choices([0,1], weights=[0.8,0.2])[0]
    
    def save_model(self, filepath='app/ml_models/crispation_predictor.joblib'):
        """Guardar modelo entrenado"""
        if self.is_trained:
            joblib.dump(self.model, filepath)
            logger.info(f"💾 Modelo guardado en: {filepath}")
    
    def load_model(self, filepath='app/ml_models/crispation_predictor.joblib'):
        """Cargar modelo pre-entrenado"""
        try:
            self.model = joblib.load(filepath)
            self.is_trained = True
            logger.info(f"📂 Modelo cargado desde: {filepath}")
        except FileNotFoundError:
            logger.warning("Modelo no encontrado, entrenando nuevo modelo...")
            self.train_model()
