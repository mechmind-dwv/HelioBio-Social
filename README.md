# 🌞 HelioBio-Social: Correlaciones Cósmicas para el Siglo XXI

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

**"Explorando correlaciones entre actividad solar y comportamiento humano con rigor científico"**

*Un proyecto de ciencia abierta para validar hipótesis heliobiológicas*

[📊 Demo](#demo) • [🚀 Instalación](#instalación) • [📖 Documentación](#documentación) • [🔬 Ciencia](#fundamentos-científicos) • [🤝 Contribuir](#contribuir)

</div>

---

## ⚠️ Aviso Científico Importante

**Este proyecto es una plataforma de investigación experimental** que busca correlaciones estadísticas entre variables solares y sociales. 

**QUÉ ES:**
- Una herramienta de análisis correlacional riguroso
- Una plataforma para generar y validar hipótesis
- Un sistema de código abierto para investigación reproducible

**QUÉ NO ES:**
- No establece causalidad definitiva
- No es astrología ni pseudociencia
- No hace predicciones deterministas sobre comportamiento individual
- No reemplaza análisis multifactoriales complejos

**Todos los hallazgos requieren validación por pares y replicación independiente.**

---

## 🌟 Visión

En 1915, Alexander Chizhevsky observó correlaciones entre ciclos solares y eventos históricos. Un siglo después, tenemos las herramientas para validar científicamente estas hipótesis.

**HelioBio-Social** es el primer sistema de código abierto que:
- ☀️ Monitorea **Actividad Solar** (manchas solares, tormentas geomagnéticas)
- 🧠 Analiza **Patrones Sociales** (tendencias en salud mental, comportamiento colectivo)
- 📊 Aplica **Análisis Científico Riguroso** (causalidad de Granger, wavelets, ML)
- 🔍 Controla **Variables Confusoras** (clima, eventos políticos, estacionalidad)

---

## 🎯 Características Principales

### 🔴 Sistema de Análisis en Tiempo Real

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  APIs Solares   │─────▶│  Motor Análisis  │─────▶│   Dashboard     │
│  (NOAA, NASA)   │      │  + Controles     │      │   Científico    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │                          │
        ▼                         ▼                          ▼
   Índice Kp              Test Granger               Visualización
   Manchas Solares        Corrección FDR             Intervalos Confianza
   Viento Solar           Validación Cruzada         Export Científico
```

### 📊 Métricas Monitorizadas

#### Actividad Solar (Datos Reales NOAA/NASA)
- **SSN** (Sunspot Number)
- **Índice Kp** (0-9, perturbaciones geomagnéticas)
- **Fulguraciones Solares** (clase X, M, C)
- **Velocidad Viento Solar** (km/s)
- **Densidad de Protones**

#### Indicadores Sociales/Salud
- **Google Trends** (términos relacionados ansiedad/depresión)
- **WHO GHO** (datos salud mental global)
- **Reddit/Twitter** (análisis sentimiento, polarización)
- **Variables Control** (clima, economía, eventos políticos)

### 🧪 Análisis Científicos Robustos

#### 1. Correlación con Controles
- Pearson/Spearman con corrección Bonferroni
- Intervalos de confianza bootstrap (95%)
- Control por variables confusoras
- Análisis de sensibilidad

#### 2. Causalidad de Granger
```python
H₀: La actividad solar NO predice indicadores sociales
H₁: La actividad solar predice indicadores sociales (α = 0.05)
```
Con validación cruzada temporal y corrección FDR.

#### 3. Análisis Wavelet
- Detección de periodicidades (ciclo 11 años, 27 días)
- Coherencia wavelet entre series
- Análisis de fase

#### 4. Machine Learning Conservador
- LSTM para detección de patrones temporales
- Validación out-of-sample estricta
- Comparación con modelos baseline
- Métricas de incertidumbre (intervalos de predicción)

---

## 🚀 Instalación Rápida

### Prerrequisitos
```bash
Python 3.9+
Node.js 16+
PostgreSQL 13+ (opcional: TimescaleDB)
Redis 6+ (opcional: para caché)
```

### Setup Completo
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/HelioBio-Social.git
cd HelioBio-Social

# 2. Setup automático (Linux/Mac)
chmod +x quickstart.sh
./quickstart.sh

# 3. O manualmente:

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python setup_db.py
uvicorn main:app --reload --port 8000

# Frontend (nueva terminal)
cd frontend
npm install
npm run dev

# Jupyter Analysis (nueva terminal)
cd analysis
pip install -r requirements.txt
jupyter lab
```

### Variables de Entorno
```bash
# .env
NOAA_API_KEY=tu_key_aqui
NASA_API_KEY=tu_key_aqui
DATABASE_URL=postgresql://user:pass@localhost/heliobio
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=opcional_para_analisis_nlp
```

---

## 📖 Uso

### 1. Dashboard Interactivo
```bash
# Inicia todo el sistema
./start_heliobio.sh

# Accede a:
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Jupyter: http://localhost:8888
```

### 2. API REST
```python
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
```

### 3. Análisis Científico
```python
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
report.save('analysis_2024.pdf')
```

---

## 🔬 Fundamentos Científicos

### Hipótesis Heliobiológica

**Propuesta Original (Chizhevsky, 1926):**
Los ciclos solares correlacionan con eventos históricos masivos.

**Hipótesis Moderna Refinada:**
Las tormentas geomagnéticas pueden correlacionar con ciertos indicadores de salud mental poblacional a través de:

1. **Mecanismos Propuestos:**
   - Alteración de ritmos circadianos (melatonina)
   - Efectos en el sistema nervioso autónomo
   - Posible influencia en neurotransmisores

2. **Variables Moderadoras:**
   - Latitud geográfica
   - Vulnerabilidad individual preexistente
   - Factores socioculturales

### Evidencia Científica Existente

| Estudio | Hallazgo | Tamaño Efecto |
|---------|----------|---------------|
| Persinger & Krippner (1989) | Correlación Kp - admisiones psiquiátricas | r ≈ 0.30 |
| Kay (2004) | Actividad solar - volatilidad mercados | Pequeño |
| Vencloviene et al. (2013) | Tormentas geomagnéticas - suicidios | OR ≈ 1.2 |

**Nota:** Estos estudios tienen limitaciones metodológicas. Nuestro objetivo es aplicar estándares modernos.

### Nuestro Enfoque Metodológico

#### Control de Sesgos
- ✅ Corrección por comparaciones múltiples (Bonferroni, FDR)
- ✅ Validación cruzada temporal
- ✅ Control de variables confusoras
- ✅ Análisis de sensibilidad
- ✅ Pre-registro de hipótesis
- ✅ Datos y código completamente abiertos

#### Limitaciones Conocidas
- Naturaleza correlacional (no causal)
- Posibles variables no controladas
- Variabilidad en calidad de datos sociales
- Necesidad de replicación independiente

---

## 🏗️ Arquitectura del Sistema

```
HelioBio-Social/
│
├── backend/                    # FastAPI + Python 3.9+
│   ├── api/v1/                # Endpoints REST
│   ├── connectors/            # APIs externas (NOAA, WHO, etc.)
│   ├── analytics/             # Motor correlacional
│   ├── ml/                    # Modelos predictivos
│   ├── database/              # PostgreSQL + TimescaleDB
│   └── tests/                 # Tests unitarios
│
├── frontend/                   # React 18 + TypeScript
│   ├── src/
│   │   ├── pages/             # Dashboard, Analysis, etc.
│   │   ├── components/        # Charts, Widgets
│   │   ├── hooks/             # Custom React hooks
│   │   └── services/          # API client
│   └── tests/
│
├── analysis/                   # Jupyter Notebooks
│   ├── notebooks/             # Análisis exploratorios
│   ├── scripts/               # Scripts batch
│   └── results/               # Plots, reportes
│
├── data/                      # Almacenamiento local
│   ├── raw/                   # Datos sin procesar
│   ├── processed/             # Datos limpios
│   └── exports/               # Datasets públicos
│
├── docs/                      # Documentación
│   ├── API_REFERENCE.md
│   ├── SCIENTIFIC_METHOD.md
│   └── papers/
│
└── deployment/                # Docker, K8s, Terraform
```

---

## 📈 Casos de Uso

### 🏛️ Para Investigadores
- Validar hipótesis heliobiológicas
- Acceder a datasets públicos curados
- Publicar estudios reproducibles
- Colaborar en análisis multidisciplinarios

### 📊 Para Científicos de Datos
- Explorar correlaciones inusuales
- Desarrollar modelos predictivos
- Practicar análisis de series temporales
- Contribuir al código del proyecto

### 🎓 Para Educación
- Enseñar análisis científico riguroso
- Demostrar importancia de controles estadísticos
- Ilustrar ciencia abierta y reproducible

### 🔍 Para Gestión de Riesgo
- Monitorear indicadores de salud poblacional
- Identificar patrones emergentes
- Planificación de recursos de salud mental

---

## 🤝 Contribuir

### Áreas de Contribución

1. **Ciencia de Datos**
   - Mejorar algoritmos de análisis
   - Implementar nuevos tests estadísticos
   - Optimizar modelos de ML

2. **Desarrollo**
   - Nuevas integraciones de APIs
   - Mejoras en UI/UX
   - Optimización de rendimiento

3. **Investigación Científica**
   - Diseñar experimentos
   - Revisar metodología
   - Escribir papers

4. **Documentación**
   - Traducir a otros idiomas
   - Crear tutoriales
   - Mejorar explicaciones

### Proceso de Contribución
```bash
# 1. Fork el repositorio
# 2. Crea una rama
git checkout -b feature/analisis-wavelets

# 3. Haz tus cambios con tests
git commit -m "feat: añade análisis wavelet para ciclos 27 días"

# 4. Push y crea Pull Request
git push origin feature/analisis-wavelets
```

---

## 📊 Roadmap 2025

### Q1 2025 - Fundamentos ✅
- [x] Sistema básico funcional
- [x] Integración NOAA/NASA
- [x] Dashboard básico
- [x] Tests de correlación

### Q2 2025 - Rigor Científico 🔄
- [ ] Pre-registro de hipótesis en OSF
- [ ] Análisis retrospectivo 2000-2024
- [ ] Paper metodológico (pre-print)
- [ ] Peer review externo

### Q3 2025 - Expansión 📅
- [ ] Más fuentes de datos (Eurostat, IHME)
- [ ] Sistema de alertas conservador
- [ ] API pública v1.0
- [ ] Colaboraciones universitarias

### Q4 2025 - Validación 🚀
- [ ] Replicación independiente
- [ ] Publicación peer-reviewed
- [ ] Open dataset público
- [ ] HelioBio Summit

---

## 🏆 Cita este Proyecto

```bibtex
@software{heliobio2025,
  author = {Tu Nombre},
  title = {HelioBio-Social: Real-Time Heliobiological Correlation Analysis},
  year = {2025},
  url = {https://github.com/tu-usuario/HelioBio-Social},
  version = {2.0.1},
  license = {MIT}
}
```

---

## 📜 Licencia

MIT License - Ciencia abierta para todos.

---

## 🙏 Agradecimientos

- **Alexander Chizhevsky** - Por la hipótesis original
- **NOAA/NASA** - Por datos solares abiertos
- **Comunidad científica** - Por metodologías robustas
- **Contribuidores** - Por mejorar el proyecto

---

## 📬 Contacto

- **GitHub**: Issues y Discussions
- **Email**: heliobio@tu-dominio.com
- **Twitter**: @HelioBioSocial

---

<div align="center">

**🌞 Ciencia abierta, rigurosa y reproducible 🌍**

⭐ Si este proyecto te parece útil, danos una estrella ⭐

*"La curiosidad científica sin rigor metodológico es pseudociencia"*

</div>
