#!/bin/bash
# Script de verificación de seguridad
# Verifica que no se subirán credenciales a GitHub

echo "🔒 Verificando seguridad del proyecto..."
echo ""

ERRORS=0
WARNINGS=0

# 1. Verificar que .env existe
echo "1️⃣  Verificando archivo .env..."
if [ -f .env ]; then
    echo "   ✅ .env existe"
else
    echo "   ⚠️  .env NO existe - copiar de .env.example"
    WARNINGS=$((WARNINGS + 1))
fi

# 2. Verificar que .env está en .gitignore
echo "2️⃣  Verificando .gitignore..."
if [ -f .gitignore ]; then
    if grep -q "^\.env$" .gitignore || grep -q "^\*\.env$" .gitignore; then
        echo "   ✅ .env está protegido en .gitignore"
    else
        echo "   ❌ .env NO está en .gitignore"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ❌ .gitignore NO existe"
    ERRORS=$((ERRORS + 1))
fi

# 3. Verificar que .env no está trackeado por git
echo "3️⃣  Verificando que .env no está en git..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "   ❌ .env está trackeado por git - ELIMINAR INMEDIATAMENTE"
    echo "      Ejecutar: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .env NO está trackeado por git"
fi

# 4. Verificar que backend/data/ está protegido
echo "4️⃣  Verificando protección de datos..."
if grep -q "backend/data/" .gitignore || grep -q "^data/" .gitignore; then
    echo "   ✅ Directorio de datos protegido"
else
    echo "   ⚠️  backend/data/ debería estar en .gitignore"
    WARNINGS=$((WARNINGS + 1))
fi

# 5. Buscar credenciales hardcodeadas en archivos Python
echo "5️⃣  Buscando credenciales en código Python..."
if grep -r "64\.23\.150\|aquicreamos\|pepito" backend/*.py backend/**/*.py 2>/dev/null | grep -v ".env\|example\|template\|test_"; then
    echo "   ⚠️  Se encontraron posibles credenciales en código Python"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ No se encontraron credenciales hardcodeadas"
fi

# 6. Verificar archivos staged para commit
echo "6️⃣  Verificando archivos staged..."
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED_FILES" ]; then
    if echo "$STAGED_FILES" | grep -q "\.env$"; then
        echo "   ❌ .env está staged para commit - REMOVER"
        echo "      Ejecutar: git reset HEAD .env"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ No hay archivos sensibles staged"
    fi
else
    echo "   ℹ️  No hay archivos staged"
fi

# 7. Verificar que .env.example no tiene credenciales reales
echo "7️⃣  Verificando .env.example..."
if [ -f .env.example ]; then
    if grep -q "64\.23\.150\|postgres:123456\|aquicreamos:pepito" .env.example; then
        echo "   ❌ .env.example contiene credenciales reales"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ .env.example está sanitizado"
    fi
else
    echo "   ⚠️  .env.example NO existe"
    WARNINGS=$((WARNINGS + 1))
fi

# 8. Verificar documentación
echo "8️⃣  Verificando documentación (MD files)..."
CREDS_IN_DOCS=$(grep -r "postgres:123456\|aquicreamos:pepito" *.md 2>/dev/null | grep -v "README_SECURITY.md\|SECURITY.md" | wc -l | tr -d ' ')
if [ "$CREDS_IN_DOCS" -gt "0" ]; then
    echo "   ⚠️  Se encontraron $CREDS_IN_DOCS posibles credenciales en .md"
    echo "      Ejecutar: ./sanitize-docs.sh"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ Documentación sanitizada"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -gt 0 ]; then
    echo "❌ ERRORES CRÍTICOS: $ERRORS"
    echo "⚠️  Warnings: $WARNINGS"
    echo ""
    echo "🚫 NO ES SEGURO HACER GIT PUSH"
    echo "   Corrige los errores antes de subir a GitHub"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "✅ Sin errores críticos"
    echo "⚠️  Warnings: $WARNINGS"
    echo ""
    echo "⚠️  Revisar warnings antes de git push"
    exit 0
else
    echo "✅ TODAS LAS VERIFICACIONES PASARON"
    echo ""
    echo "🚀 SEGURO PARA GIT PUSH"
    exit 0
fi
