#!/bin/bash

# Script para detener servicios

echo "Deteniendo servicios Spark MLflow..."
docker-compose down

echo ""
echo "✓ Servicios detenidos!"
echo ""
echo "Para eliminar también los volúmenes (ADVERTENCIA: se perderán los datos):"
echo "  docker-compose down -v"
echo ""
