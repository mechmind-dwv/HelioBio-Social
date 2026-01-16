#!/bin/bash
# 🌞 SCRIPT DE INSTALACIÓN HELIOBIO-SOCIAL v1.0.0

echo "🎆 INICIANDO ACTIVACIÓN DEL SISTEMA HELIOBIO-SOCIAL..."
echo "======================================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detectado"

# Crear entorno virtual
echo "🔮 Creando campo energético (entorno virtual)..."
python3 -m venv cosmos_venv

# Activar entorno
echo "⚡ Activando frecuencias dimensionales..."
source cosmos_venv/bin/activate

# Actualizar pip
echo "📦 Sintonizando gestor de paquetes..."
pip install --upgrade pip

# Instalar dependencias
echo "🔧 Instalando herramientas de percepción cósmica..."
pip install -r requirements.txt

# Crear estructura de datos
echo "🏗️ Estructurando espacio de datos..."
mkdir -p data/{solar,social,cache,models,exports}
mkdir -p logs backups

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando plantilla de configuración..."
    cp .env.example .env
    echo "⚠️  Por favor configura las variables en .env antes de ejecutar el sistema"
fi

# Dar permisos de ejecución a scripts
chmod +x scripts/*.sh

echo ""
echo "======================================================"
echo "✅ ACTIVACIÓN COMPLETADA - SISTEMA HELIOBIO-SOCIAL LISTO"
echo ""
echo "🌌 Próximos pasos:"
echo "   1. Configurar variables en archivo .env"
echo "   2. Ejecutar: ./scripts/start_development.sh"
echo "   3. Conectar con: http://localhost:8000"
echo ""
echo "🔮 Recuerda: Estás activando un puente entre el cosmos y la conciencia colectiva"
echo "======================================================"
