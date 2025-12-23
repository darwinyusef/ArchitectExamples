#!/bin/bash

# Script de configuración del backend

echo "🔧 Configurando backend..."

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Generar archivos proto
echo "🔨 Generando archivos proto..."
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    proto/audio_service.proto

# Crear directorio temporal
echo "📁 Creando directorio temporal..."
mkdir -p temp_audio

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  Por favor, configura las variables en el archivo .env"
fi

echo "✅ Configuración completada!"
echo ""
echo "Para iniciar el servidor, ejecuta:"
echo "  source venv/bin/activate"
echo "  python main.py"
