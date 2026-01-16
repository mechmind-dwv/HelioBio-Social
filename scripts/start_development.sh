#!/bin/bash
# 🚀 SCRIPT DE INICIO DESARROLLO HELIOBIO-SOCIAL

echo "🌞 INICIANDO SISTEMA HELIOBIO-SOCIAL EN MODO DESARROLLO..."
echo "=========================================================="

# Verificar si el entorno está activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔮 Activando campo energético..."
    source cosmos_venv/bin/activate
fi

# Verificar archivo .env
if [ ! -f .env ]; then
    echo "❌ Archivo .env no encontrado. Copia .env.example y configura tus variables."
    exit 1
fi

# Crear logs si no existen
mkdir -p logs

echo "📍 Iniciando servidor de conciencia en http://localhost:8000"
echo "📊 Dashboard disponible en http://localhost:8000/docs"
echo ""
echo "🛑 Presiona Ctrl+C para detener el sistema"
echo "=========================================================="

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
