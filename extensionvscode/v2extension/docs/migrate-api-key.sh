#!/bin/bash

# Script para migrar OpenAI API Key desde v1extension
# Uso: ./migrate-api-key.sh

set -e

echo "🔑 Migración de OpenAI API Key desde v1extension"
echo "================================================"
echo ""

# Verificar que estamos en v2extension
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Ejecutar desde v2extension/"
    exit 1
fi

# Buscar API key en v1extension
echo "📍 Buscando OpenAI API Key en v1extension..."

V1_SETTINGS="../v1extension/settings.example.json"
V1_USER_SETTINGS="$HOME/.config/Code/User/settings.json"  # Linux/macOS
V1_USER_SETTINGS_MAC="$HOME/Library/Application Support/Code/User/settings.json"  # macOS

API_KEY=""

# Método 1: Desde settings.example.json de v1
if [ -f "$V1_SETTINGS" ]; then
    echo "   Verificando $V1_SETTINGS..."
    API_KEY=$(grep -o '"aiGoalsTracker.openaiApiKey": *"sk-[^"]*"' "$V1_SETTINGS" 2>/dev/null | cut -d'"' -f4 || echo "")

    if [ -n "$API_KEY" ] && [ "$API_KEY" != "sk-proj-TU_API_KEY_AQUI" ]; then
        echo "   ✅ API Key encontrada en settings.example.json"
    else
        API_KEY=""
    fi
fi

# Método 2: Desde VS Code User Settings (macOS)
if [ -z "$API_KEY" ] && [ -f "$V1_USER_SETTINGS_MAC" ]; then
    echo "   Verificando VS Code settings (macOS)..."
    API_KEY=$(grep -o '"aiGoalsTracker.openaiApiKey": *"sk-[^"]*"' "$V1_USER_SETTINGS_MAC" 2>/dev/null | cut -d'"' -f4 || echo "")

    if [ -n "$API_KEY" ]; then
        echo "   ✅ API Key encontrada en VS Code settings"
    fi
fi

# Método 3: Desde VS Code User Settings (Linux)
if [ -z "$API_KEY" ] && [ -f "$V1_USER_SETTINGS" ]; then
    echo "   Verificando VS Code settings (Linux)..."
    API_KEY=$(grep -o '"aiGoalsTracker.openaiApiKey": *"sk-[^"]*"' "$V1_USER_SETTINGS" 2>/dev/null | cut -d'"' -f4 || echo "")

    if [ -n "$API_KEY" ]; then
        echo "   ✅ API Key encontrada en VS Code settings"
    fi
fi

# Si no se encontró, pedir al usuario
if [ -z "$API_KEY" ]; then
    echo ""
    echo "⚠️  No se encontró OpenAI API Key automáticamente"
    echo ""
    echo "Buscar manualmente en:"
    echo "  1. VS Code → Settings → buscar 'aiGoalsTracker.openaiApiKey'"
    echo "  2. v1extension/settings.example.json"
    echo ""
    read -p "Ingresar OpenAI API Key manualmente (sk-...): " API_KEY

    if [ -z "$API_KEY" ]; then
        echo "❌ No se proporcionó API Key"
        exit 1
    fi
fi

# Validar formato de API key
if [[ ! "$API_KEY" =~ ^sk- ]]; then
    echo "❌ API Key inválida (debe empezar con 'sk-')"
    exit 1
fi

echo ""
echo "✅ API Key obtenida: ${API_KEY:0:10}...${API_KEY: -4}"
echo ""

# Crear o actualizar .env
if [ ! -f ".env" ]; then
    echo "📝 Creando .env desde .env.example..."
    cp .env.example .env
fi

# Actualizar OPENAI_API_KEY en .env
if grep -q "^OPENAI_API_KEY=" .env; then
    echo "📝 Actualizando OPENAI_API_KEY en .env..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" .env
    else
        # Linux
        sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" .env
    fi
else
    echo "📝 Agregando OPENAI_API_KEY a .env..."
    echo "OPENAI_API_KEY=$API_KEY" >> .env
fi

# Generar SECRET_KEY si no existe
if grep -q "^SECRET_KEY=your-secret-key" .env; then
    echo "🔐 Generando SECRET_KEY..."
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        else
            sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        fi
        echo "   ✅ SECRET_KEY generada"
    else
        echo "   ⚠️  openssl no disponible, usar un string de 32+ caracteres"
    fi
fi

# También actualizar backend/.env si existe
if [ -f "backend/.env" ]; then
    echo "📝 Actualizando backend/.env..."
    if grep -q "^OPENAI_API_KEY=" backend/.env; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" backend/.env
        else
            sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" backend/.env
        fi
    else
        echo "OPENAI_API_KEY=$API_KEY" >> backend/.env
    fi
fi

echo ""
echo "=" * 60
echo "✅ Migración Completada"
echo "=" * 60
echo ""
echo "📋 Archivos actualizados:"
echo "   - .env"
[ -f "backend/.env" ] && echo "   - backend/.env"
echo ""
echo "🔑 OpenAI API Key: ${API_KEY:0:10}...${API_KEY: -4}"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Verificar .env:"
echo "      cat .env | grep OPENAI_API_KEY"
echo ""
echo "   2. Iniciar servicios:"
echo "      ./start-with-remote-redis.sh"
echo ""
echo "   3. Probar backend:"
echo "      curl http://localhost:8000/health"
echo ""
