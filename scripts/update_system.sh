#!/bin/bash
# 🔄 SCRIPT DE ACTUALIZACIÓN HELIOBIO-SOCIAL v1.3.0

echo "🔄 ACTUALIZANDO SISTEMA HELIOBIO-SOCIAL A v1.3.0..."
echo "===================================================="

# Verificar que el entorno virtual esté activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔮 Activando entorno virtual..."
    source venv/bin/activate
fi

# Actualizar dependencias
echo "📦 Actualizando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "🏗️ Creando estructura de directorios..."
mkdir -p logs backups docs

# Verificar que todos los componentes estén presentes
echo "🔍 Verificando componentes del sistema..."
python -c "
try:
    from app.core.alert_system import AlertSystem
    from app.ml_models.crispation_predictor import CrispationPredictor
    print('✅ Todos los componentes importados correctamente')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
"

# Ejecutar tests básicos
echo "🧪 Ejecutando verificaciones del sistema..."
python -c "
import asyncio
async def test_system():
    from app.core.alert_system import AlertSystem
    alert_system = AlertSystem()
    print('✅ Sistema de alertas: OK')
    
    # Verificar que se pueden crear alertas
    from datetime import datetime
    from app.core.alert_system import Alert, AlertLevel, AlertType
    
    test_alert = Alert(
        id=1,
        level=AlertLevel.INFO,
        type=AlertType.SYSTEM,
        title='Test Alert',
        message='System test successful',
        timestamp=datetime.utcnow(),
        duration_hours=1
    )
    print('✅ Creación de alertas: OK')
    print('🎉 Sistema listo para v1.3.0!')

asyncio.run(test_system())
"

echo ""
echo "===================================================="
echo "✅ ACTUALIZACIÓN COMPLETADA - HELIOBIO-SOCIAL v1.3.0"
echo ""
echo "🚀 Para iniciar el sistema:"
echo "   ./scripts/start_development.sh"
echo ""
echo "📊 Dashboard disponible en: http://localhost:8000"
echo "📚 Documentación API en: http://localhost:8000/docs"
echo "===================================================="
