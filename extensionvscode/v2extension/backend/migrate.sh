#!/bin/bash
# Script para ejecutar migraciones de Alembic

set -e  # Exit on error

echo "🗄️  Migraciones de Base de Datos - AI Goals Tracker V2"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "alembic.ini" ]; then
    echo "❌ Error: Ejecutar desde directorio backend/"
    echo "   cd backend && ./migrate.sh"
    exit 1
fi

# Verificar que .env existe
if [ ! -f "../.env" ]; then
    echo "❌ Error: No se encontró archivo .env"
    echo "   Copiar .env.example a .env y configurar DATABASE_URL"
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: ./migrate.sh [comando]

Comandos disponibles:
  upgrade       Aplicar todas las migraciones (alembic upgrade head)
  downgrade     Revertir una migración (alembic downgrade -1)
  current       Mostrar revisión actual (alembic current)
  history       Mostrar historial de migraciones (alembic history)
  create        Crear nueva migración (requiere mensaje)
  reset         PELIGRO: Eliminar y recrear toda la DB
  help          Mostrar esta ayuda

Ejemplos:
  ./migrate.sh upgrade
  ./migrate.sh downgrade
  ./migrate.sh current
  ./migrate.sh history
  ./migrate.sh create "add new field"
  ./migrate.sh reset

EOF
}

# Verificar PostgreSQL
check_postgres() {
    echo "🔍 Verificando PostgreSQL..."

    # Extraer credenciales del .env
    DB_URL=$(grep "^DATABASE_URL=" ../.env | cut -d '=' -f2)

    if [ -z "$DB_URL" ]; then
        echo "❌ Error: DATABASE_URL no configurado en .env"
        exit 1
    fi

    echo "   ✅ DATABASE_URL configurado"
}

# Comando principal
COMMAND=${1:-help}

case "$COMMAND" in
    upgrade)
        echo "📤 Aplicando migraciones..."
        check_postgres
        poetry run alembic upgrade head
        echo ""
        echo "✅ Migraciones aplicadas exitosamente"
        ;;

    downgrade)
        echo "📥 Revirtiendo última migración..."
        check_postgres
        poetry run alembic downgrade -1
        echo ""
        echo "✅ Migración revertida"
        ;;

    current)
        echo "📍 Revisión actual:"
        poetry run alembic current
        ;;

    history)
        echo "📜 Historial de migraciones:"
        poetry run alembic history --verbose
        ;;

    create)
        if [ -z "$2" ]; then
            echo "❌ Error: Proporcionar mensaje para la migración"
            echo "   Uso: ./migrate.sh create \"mensaje de la migración\""
            exit 1
        fi
        echo "📝 Creando nueva migración..."
        poetry run alembic revision --autogenerate -m "$2"
        echo ""
        echo "✅ Migración creada"
        ;;

    reset)
        echo "⚠️  PELIGRO: Esto eliminará TODOS los datos"
        echo ""
        read -p "¿Estás seguro? Escribe 'yes' para continuar: " confirm

        if [ "$confirm" != "yes" ]; then
            echo "❌ Operación cancelada"
            exit 0
        fi

        echo ""
        echo "🔄 Revirtiendo todas las migraciones..."
        check_postgres
        poetry run alembic downgrade base

        echo ""
        echo "📤 Aplicando todas las migraciones de nuevo..."
        poetry run alembic upgrade head

        echo ""
        echo "✅ Base de datos reiniciada"
        ;;

    help)
        show_help
        ;;

    *)
        echo "❌ Comando desconocido: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
