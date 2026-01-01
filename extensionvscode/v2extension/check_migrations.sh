#!/bin/bash
# Script para verificar el estado de las migraciones en PostgreSQL

echo "============================================"
echo "Verificación de Migraciones - PostgreSQL"
echo "============================================"
echo ""

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo"
    echo "Por favor inicia Docker Desktop y vuelve a ejecutar este script"
    exit 1
fi

echo "✓ Docker está corriendo"
echo ""

# Verificar si los servicios están levantados
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Los servicios no están corriendo"
    echo "Levantando servicios..."
    docker-compose up -d
    echo "Esperando a que PostgreSQL esté listo..."
    sleep 10
fi

echo "✓ Servicios corriendo"
echo ""

# Verificar conexión a PostgreSQL
echo "1. Verificando conexión a PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "   ✓ PostgreSQL está listo"
else
    echo "   ❌ PostgreSQL no responde"
    exit 1
fi

echo ""

# Verificar si la base de datos existe
echo "2. Verificando base de datos 'ai_goals_tracker'..."
if docker-compose exec -T postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw ai_goals_tracker; then
    echo "   ✓ Base de datos existe"
else
    echo "   ❌ Base de datos no existe"
    echo "   Creando base de datos..."
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE ai_goals_tracker;"
fi

echo ""

# Verificar extensión pgvector
echo "3. Verificando extensión pgvector..."
VECTOR_CHECK=$(docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -tAc "SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
if [ "$VECTOR_CHECK" = "1" ]; then
    echo "   ✓ pgvector está instalado"
else
    echo "   ⚠️  pgvector no está instalado"
    echo "   Instalando pgvector..."
    docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
    echo "   ✓ pgvector instalado"
fi

echo ""

# Verificar tabla alembic_version
echo "4. Verificando tabla de versiones de Alembic..."
ALEMBIC_TABLE=$(docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'alembic_version';")
if [ "$ALEMBIC_TABLE" = "1" ]; then
    echo "   ✓ Tabla alembic_version existe"

    # Ver versión actual
    CURRENT_VERSION=$(docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -tAc "SELECT version_num FROM alembic_version;")
    if [ -n "$CURRENT_VERSION" ]; then
        echo "   ✓ Versión actual: $CURRENT_VERSION"
    else
        echo "   ⚠️  No hay migraciones aplicadas"
    fi
else
    echo "   ⚠️  Tabla alembic_version no existe"
    echo "   → Las migraciones NO se han ejecutado"
fi

echo ""

# Listar todas las tablas
echo "5. Listando tablas existentes..."
TABLES=$(docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -tAc "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")

if [ -z "$TABLES" ]; then
    echo "   ⚠️  No hay tablas en la base de datos"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  MIGRACIONES NO EJECUTADAS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Para ejecutar las migraciones:"
    echo ""
    echo "  docker-compose exec backend alembic upgrade head"
    echo ""
    echo "O reinicia el backend (las migraciones se ejecutan automáticamente):"
    echo ""
    echo "  docker-compose restart backend"
    echo "  docker-compose logs -f backend"
    echo ""
else
    echo "   Tablas encontradas:"
    echo "$TABLES" | while read -r table; do
        echo "     • $table"
    done

    # Contar tablas
    TABLE_COUNT=$(echo "$TABLES" | grep -v "^$" | wc -l | tr -d ' ')

    echo ""
    echo "   Total: $TABLE_COUNT tablas"

    # Verificar las 8 tablas esperadas
    EXPECTED_TABLES=("users" "courses" "goals" "tasks" "code_snapshots" "events" "embeddings" "rate_limit_audits")
    MISSING_TABLES=()

    for table in "${EXPECTED_TABLES[@]}"; do
        if ! echo "$TABLES" | grep -qw "$table"; then
            MISSING_TABLES+=("$table")
        fi
    done

    echo ""
    if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ TODAS LAS MIGRACIONES EJECUTADAS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Las 8 tablas esperadas están presentes:"
        for table in "${EXPECTED_TABLES[@]}"; do
            echo "  ✓ $table"
        done
    else
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  FALTAN ALGUNAS TABLAS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Tablas faltantes:"
        for table in "${MISSING_TABLES[@]}"; do
            echo "  ✗ $table"
        done
        echo ""
        echo "Ejecuta las migraciones:"
        echo "  docker-compose exec backend alembic upgrade head"
    fi
fi

echo ""

# Verificar datos en las tablas (si existen)
if [ "$TABLE_COUNT" -ge 8 ]; then
    echo "6. Verificando datos en las tablas..."

    for table in goals tasks users courses code_snapshots events embeddings rate_limit_audits; do
        if echo "$TABLES" | grep -qw "$table"; then
            COUNT=$(docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -tAc "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "0")
            echo "   • $table: $COUNT registros"
        fi
    done
fi

echo ""
echo "============================================"
echo "Verificación completa"
echo "============================================"
