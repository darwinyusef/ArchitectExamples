#!/bin/bash

# Script para iniciar AI Goals Tracker V2 con Redis remoto
# Uso: ./start-with-remote-redis.sh

set -e

echo "🚀 AI Goals Tracker V2 - Inicio con Redis Remoto"
echo "================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml no encontrado"
    echo "   Ejecutar desde la raíz de v2extension/"
    exit 1
fi

# Paso 1: Verificar .env
echo "📋 Paso 1: Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado, creando desde .env.example..."
    cp .env.example .env
    echo "✅ .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita .env y agrega:"
    echo "   - OPENAI_API_KEY"
    echo "   - SECRET_KEY"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
else
    echo "✅ .env encontrado"
fi

# Paso 2: Verificar Redis remoto
echo ""
echo "🔌 Paso 2: Probando conexión a Redis remoto..."
REDIS_HOST="64.23.150.221"
REDIS_PORT="6379"

# Verificar si redis-cli está instalado
if command -v redis-cli &> /dev/null; then
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT PING &> /dev/null; then
        echo "✅ Redis remoto accesible ($REDIS_HOST:$REDIS_PORT)"
    else
        echo "❌ Error: No se puede conectar a Redis remoto"
        echo "   Verifica que $REDIS_HOST:$REDIS_PORT esté accesible"
        exit 1
    fi
else
    echo "⚠️  redis-cli no instalado, saltando test de conectividad"
    echo "   Instalar con: brew install redis (macOS) o apt install redis-tools (Linux)"
fi

# Paso 3: Verificar Docker
echo ""
echo "🐳 Paso 3: Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está corriendo"
    echo "   Inicia Docker Desktop y vuelve a intentar"
    exit 1
fi
echo "✅ Docker está corriendo"

# Paso 4: Detener servicios previos
echo ""
echo "🛑 Paso 4: Deteniendo servicios previos (si existen)..."
docker-compose down 2>/dev/null || true
echo "✅ Servicios previos detenidos"

# Paso 5: Iniciar servicios (SIN Redis local)
echo ""
echo "🚀 Paso 5: Iniciando servicios..."
echo "   - PostgreSQL"
echo "   - RabbitMQ"
echo "   - MinIO"
echo "   - Backend API"
echo "   (Redis remoto se usará: $REDIS_HOST:$REDIS_PORT)"
echo ""

# Exportar REDIS_URL para docker-compose
export REDIS_URL="redis://$REDIS_HOST:$REDIS_PORT/0"

docker-compose up -d

# Paso 6: Esperar a que los servicios estén healthy
echo ""
echo "⏳ Paso 6: Esperando a que los servicios estén listos..."
echo "   Esto puede tomar 30-60 segundos..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))

    # Verificar PostgreSQL
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo "   ✅ PostgreSQL listo"
        break
    fi

    echo "   ⏳ Intento $attempt/$max_attempts..."
    sleep 2
done

# Dar tiempo adicional para que backend inicie
sleep 5

# Paso 7: Verificar servicios
echo ""
echo "🔍 Paso 7: Verificando servicios..."

# Health check del backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API respondiendo"

    # Health check detallado
    echo ""
    echo "📊 Estado de servicios:"
    curl -s http://localhost:8000/api/v1/health/detailed | python3 -m json.tool 2>/dev/null || echo "⚠️  No se pudo obtener estado detallado"
else
    echo "❌ Backend no responde en http://localhost:8000"
    echo ""
    echo "Ver logs con: docker-compose logs backend"
fi

# Paso 8: Mostrar información útil
echo ""
echo "=" * 60
echo "✅ ¡AI Goals Tracker V2 está corriendo!"
echo "=" * 60
echo ""
echo "🌐 URLs disponibles:"
echo "   - Backend API:      http://localhost:8000"
echo "   - API Docs:         http://localhost:8000/docs"
echo "   - Health Check:     http://localhost:8000/health"
echo "   - RabbitMQ UI:      http://localhost:15672 (guest/guest)"
echo "   - MinIO Console:    http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "🔌 Redis Remoto:"
echo "   - Host: $REDIS_HOST"
echo "   - Port: $REDIS_PORT"
echo "   - Conectar: redis-cli -h $REDIS_HOST -p $REDIS_PORT"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Probar conexión WebSocket:"
echo "      websocat 'ws://localhost:8000/api/v1/ws?token=test'"
echo ""
echo "   2. Ver logs en tiempo real:"
echo "      docker-compose logs -f backend"
echo ""
echo "   3. Probar Redis remoto:"
echo "      python backend/scripts/test_redis.py"
echo ""
echo "   4. Iniciar frontend (VS Code extension):"
echo "      cd frontend && npm install && npm run compile"
echo "      code . (presionar F5)"
echo ""
echo "🛑 Para detener:"
echo "   docker-compose down"
echo ""
