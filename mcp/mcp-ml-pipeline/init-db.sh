#!/bin/bash
set -e

# Crear base de datos para MLflow
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE mlflow;
    GRANT ALL PRIVILEGES ON DATABASE mlflow TO airflow;
EOSQL

echo "Base de datos MLflow creada exitosamente"
