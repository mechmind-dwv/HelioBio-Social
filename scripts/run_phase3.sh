#!/bin/bash
# scripts/run_phase3.sh

echo "🚀 INICIANDO FASE 3: VALIDACIÓN ACADÉMICA COMPLETA"
echo "=================================================="

# 1. Construir dataset científico
echo "📊 1. Construyendo dataset científico (2010-2025)..."
python analysis/scripts/historical_data_pipeline.py

# 2. Ejecutar análisis científico
echo "🔬 2. Ejecutando análisis científico completo..."
jupyter nbconvert --execute --to notebook \
  analysis/notebooks/01_scientific_validation.ipynb \
  --output analysis/results/validation_executed.ipynb

# 3. Generar paper LaTeX
echo "📝 3. Generando paper científico en LaTeX..."
cd docs/papers
pdflatex heliobio_scientific_paper.tex
pdflatex heliobio_scientific_paper.tex  # Segunda pasada para referencias
cd ../..

# 4. Iniciar API pública
echo "🌐 4. Iniciando API pública para investigadores..."
docker-compose -f docker-compose.scientific.yml up -d api-public

# 5. Iniciar entorno Jupyter
echo "🐳 5. Iniciando entorno científico reproducible..."
docker-compose -f docker-compose.scientific.yml up -d jupyter-scientific

# 6. Generar reporte final
echo "📋 6. Generando reporte final de validación..."
python analysis/scripts/generate_validation_report.py

echo ""
echo "✅ FASE 3 COMPLETADA"
echo "===================="
echo ""
echo "Acceso a los recursos:"
echo "• 📊 Dataset científico: data/scientific/"
echo "• 📝 Paper PDF: docs/papers/heliobio_scientific_paper.pdf"
echo "• 🌐 API pública: http://localhost:8080/docs"
echo "• 🐳 Jupyter Lab: http://localhost:8888 (token: heliobio)"
echo "• 📋 Reporte: analysis/results/reports/"
echo ""
echo "Para citar este trabajo:"
echo "HelioBio-Social Research Team. (2025). HelioBio-Social Scientific Dataset v1.0."
echo "https://doi.org/10.5281/zenodo.xxxxxxx"
