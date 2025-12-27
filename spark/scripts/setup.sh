#!/bin/bash

# Script de setup para el proyecto Spark MLflow

set -e

echo "========================================="
echo "Spark MLflow Learning Examples - Setup"
echo "========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
echo "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Por favor instala Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker instalado${NC}"

# Verificar Docker Compose
echo "Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose instalado${NC}"

# Crear directorios necesarios
echo ""
echo "Creando directorios..."
mkdir -p data/raw data/processed logs airflow/{dags,logs,plugins}
echo -e "${GREEN}✓ Directorios creados${NC}"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo ""
    echo "Creando archivo .env..."
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠ Por favor revisa y edita .env con tus configuraciones${NC}"
fi

# Crear archivos .gitkeep
touch data/raw/.gitkeep data/processed/.gitkeep logs/.gitkeep

# Iniciar servicios con Docker Compose
echo ""
echo "¿Deseas iniciar los servicios con Docker Compose? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "Iniciando servicios..."
    docker-compose up -d

    echo ""
    echo "Esperando a que los servicios estén listos..."
    sleep 10

    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ Setup completado!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "Servicios disponibles:"
    echo "  • MLflow UI:      http://localhost:5000"
    echo "  • Airflow UI:     http://localhost:8080 (admin/admin)"
    echo "  • PgAdmin:        http://localhost:5050 (admin@example.com/admin)"
    echo "  • PostgreSQL:     localhost:5432"
    echo ""
    echo "Para ver los logs:"
    echo "  docker-compose logs -f [servicio]"
    echo ""
    echo "Para detener los servicios:"
    echo "  docker-compose down"
    echo ""
else
    echo ""
    echo -e "${YELLOW}Servicios no iniciados. Para iniciar manualmente:${NC}"
    echo "  docker-compose up -d"
fi

echo ""
echo "Siguiente paso: Instalar dependencias Python"
echo "  pip install -r requirements.txt"
echo ""
echo "Luego abre Jupyter Notebook:"
echo "  jupyter notebook"
echo ""
