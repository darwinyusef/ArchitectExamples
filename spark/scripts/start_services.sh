#!/bin/bash

# Script para iniciar servicios

echo "Iniciando servicios Spark MLflow..."
docker-compose up -d

echo ""
echo "Esperando a que los servicios estén listos..."
sleep 15

echo ""
echo "Estado de los servicios:"
docker-compose ps

echo ""
echo "✓ Servicios iniciados!"
echo ""
echo "Servicios disponibles:"
echo "  • MLflow UI:      http://localhost:5000"
echo "  • Airflow UI:     http://localhost:8080 (admin/admin)"
echo "  • PgAdmin:        http://localhost:5050"
echo "  • PostgreSQL:     localhost:5432"
echo ""
