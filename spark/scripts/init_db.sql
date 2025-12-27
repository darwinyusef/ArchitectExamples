-- Script de inicialización de base de datos
-- Este script se ejecuta automáticamente al iniciar PostgreSQL

-- Crear base de datos para MLflow
CREATE DATABASE mlflow_db;

-- Crear base de datos para Airflow
CREATE DATABASE airflow_db;

-- Base de datos principal ya existe (spark_ml_db)

-- Crear tablas de ejemplo
\c spark_ml_db;

-- Tabla para resultados de clustering
CREATE TABLE IF NOT EXISTS customer_clusters (
    customer_id INTEGER PRIMARY KEY,
    cluster INTEGER NOT NULL,
    feature_0 DOUBLE PRECISION,
    feature_1 DOUBLE PRECISION,
    feature_2 DOUBLE PRECISION,
    feature_3 DOUBLE PRECISION,
    feature_4 DOUBLE PRECISION,
    feature_5 DOUBLE PRECISION,
    feature_6 DOUBLE PRECISION,
    feature_7 DOUBLE PRECISION,
    feature_8 DOUBLE PRECISION,
    feature_9 DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para estadísticas de clusters
CREATE TABLE IF NOT EXISTS cluster_statistics (
    cluster INTEGER PRIMARY KEY,
    num_customers INTEGER,
    avg_feature_0 DOUBLE PRECISION,
    avg_feature_1 DOUBLE PRECISION,
    avg_feature_2 DOUBLE PRECISION,
    avg_feature_3 DOUBLE PRECISION,
    avg_feature_4 DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para tracking de experimentos
CREATE TABLE IF NOT EXISTS experiment_runs (
    run_id VARCHAR(255) PRIMARY KEY,
    experiment_name VARCHAR(255),
    model_type VARCHAR(100),
    accuracy DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_cluster ON customer_clusters(cluster);
CREATE INDEX idx_created_at ON customer_clusters(created_at);

-- Grants
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spark_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spark_user;
