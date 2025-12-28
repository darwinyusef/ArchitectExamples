#!/bin/bash
# Script para sanitizar credenciales en documentación
# Reemplaza credenciales reales con placeholders

echo "🔒 Sanitizando credenciales en documentación..."
echo ""

# Archivos a sanitizar (todos los .md excepto SECURITY.md)
FILES=(
    "README.md"
    "README_FINAL.md"
    "README_REDIS.md"
    "CONFIGURACION_ACTUAL.md"
    "INICIO_RAPIDO.md"
    "SETUP_COMPLETO.md"
    "SETUP_CON_POSTGRES_LOCAL.md"
    "RESUMEN_COMPLETO.md"
    "FINAL_SUMMARY.md"
    "DEPLOYMENT_OPTIONS.md"
    "REDIS_SETUP.md"
)

# Contador de cambios
CHANGES=0

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 Procesando: $file"

        # Crear backup
        cp "$file" "$file.bak"

        # Reemplazos de credenciales
        sed -i '' \
            -e 's/64\.23\.150\.221/YOUR_REDIS_OR_RABBITMQ_HOST/g' \
            -e 's/postgres\/123456/YOUR_DB_USER\/YOUR_DB_PASSWORD/g' \
            -e 's/postgres:123456/YOUR_DB_USER:YOUR_DB_PASSWORD/g' \
            -e 's/aquicreamos\/pepito/YOUR_RABBITMQ_USER\/YOUR_RABBITMQ_PASSWORD/g' \
            -e 's/aquicreamos:pepito/YOUR_RABBITMQ_USER:YOUR_RABBITMQ_PASSWORD/g' \
            -e 's/User: postgres/User: YOUR_DB_USER/g' \
            -e 's/Pass: 123456/Pass: YOUR_DB_PASSWORD/g' \
            -e 's/User: aquicreamos/User: YOUR_RABBITMQ_USER/g' \
            -e 's/Pass: pepito/Pass: YOUR_RABBITMQ_PASSWORD/g' \
            -e 's/-U postgres/-U YOUR_DB_USER/g' \
            -e 's/psql -U postgres/psql -U YOUR_DB_USER/g' \
            -e 's/createdb -U postgres/createdb -U YOUR_DB_USER/g' \
            "$file"

        # Comparar cambios
        if ! diff -q "$file" "$file.bak" > /dev/null 2>&1; then
            CHANGES=$((CHANGES + 1))
            echo "   ✅ Sanitizado"
        else
            echo "   ℹ️  Sin cambios necesarios"
        fi

        # Eliminar backup
        rm "$file.bak"
    else
        echo "   ⚠️  Archivo no encontrado: $file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Sanitización completa"
echo "   Archivos modificados: $CHANGES"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Revisar cambios con: git diff"
echo "   - El archivo .env contiene las credenciales reales"
echo "   - .env está protegido en .gitignore"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
