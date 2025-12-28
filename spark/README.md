# Spark MLflow Learning Examples

Proyecto de aprendizaje de Apache Spark integrado con MLflow y diferentes frameworks de Machine Learning.

## Estructura del Proyecto

```
spark/
├── notebooks/           # Jupyter notebooks con ejemplos prácticos
│   ├── 01_spark_airflow_mlflow.ipynb
│   ├── 02_spark_pytorch_mlflow.ipynb
│   ├── 03_spark_tensorflow_mlflow.ipynb
│   ├── 04_spark_sklearn_mlflow.ipynb
│   ├── 05_spark_scipy_mathematics.ipynb
│   ├── 06_spark_clustering_postgres.ipynb
│   ├── 07_mlflow_visualizations.ipynb
│   └── 08_proyecto_final_integracion.ipynb   ⭐ PROYECTO FINAL
├── data/               # Datos para los ejemplos
│   ├── raw/           # Datos sin procesar
│   └── processed/     # Datos procesados
├── scripts/           # Scripts auxiliares
├── config/            # Configuraciones
├── logs/              # Logs de ejecución
├── docker-compose.yml # Servicios (MLflow, Postgres, Airflow)
└── requirements.txt   # Dependencias Python
```

## Notebooks Disponibles

### 1. Spark + Airflow + MLflow
- Orquestación de pipelines de datos con Airflow
- Tracking de experimentos con MLflow
- Ejecución distribuida con Spark

### 2. Spark + PyTorch + MLflow
- Deep Learning distribuido con PyTorch y Spark
- Entrenamiento de redes neuronales
- Versionado de modelos con MLflow

### 3. Spark + TensorFlow + MLflow
- Integración de TensorFlow con Spark
- Procesamiento de datos a escala
- Registro de métricas y modelos

### 4. Spark + Scikit-learn + MLflow
- Machine Learning clásico con Spark ML y Sklearn
- Pipelines de ML distribuidos
- Comparación de modelos

### 5. Spark + SciPy + Matemáticas para ML
- Operaciones matemáticas avanzadas
- Optimización y estadística
- Álgebra lineal distribuida

### 6. Spark + Clustering + PostgreSQL
- Modelos de clustering (K-Means, DBSCAN, etc.)
- Almacenamiento en PostgreSQL
- Análisis de grandes volúmenes de datos

### 7. MLflow + Visualizaciones (Matplotlib & Seaborn)
- Integración de gráficos con MLflow
- Visualizaciones estáticas e interactivas
- Confusion matrix, ROC curves, Feature importance
- Dashboards con Plotly
- Best practices de visualización en ML

### 8. ⭐ PROYECTO FINAL: Sistema de Detección de Fraude End-to-End
**Integración completa de todas las tecnologías**
- ✅ Spark (procesamiento distribuido)
- ✅ MLflow (tracking y gestión de modelos)
- ✅ Airflow (orquestación de pipelines)
- ✅ Scikit-learn (modelos de ML)
- ✅ SciPy (análisis estadístico)
- ✅ PostgreSQL (almacenamiento de datos)
- ✅ Parquet (formato de datos eficiente)
- ✅ Matplotlib/Seaborn (visualizaciones)
- ✅ MLOps (best practices de producción)

**Pipeline completo de 13 pasos:**
1. Setup e inicialización
2. Generación de datos sintéticos
3. Almacenamiento en PostgreSQL
4. Procesamiento con Spark y Parquet
5. Análisis exploratorio con SciPy
6. Feature engineering
7. Preparación de datos para ML
8. Entrenamiento de modelos
9. Comparación y selección
10. Evaluación detallada
11. Guardado de resultados
12. Resumen y MLOps
13. Automatización con Airflow

📖 Ver [PROYECTO_FINAL.md](PROYECTO_FINAL.md) para documentación completa

## Instalación

### Requisitos Previos
- Python 3.8+
- Java 8 o 11
- Docker y Docker Compose (opcional, para servicios)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Iniciar Servicios con Docker

```bash
docker-compose up -d
```

Esto iniciará:
- MLflow UI: http://localhost:5000
- PostgreSQL: localhost:5432
- Airflow: http://localhost:8080
- PgAdmin: http://localhost:5050
- Grafana: http://localhost:3000 (admin/admin)

## Uso

1. Iniciar Jupyter Notebook:
```bash
jupyter notebook
```

2. Navegar a la carpeta `notebooks/`

3. Abrir cualquier notebook y ejecutar las celdas secuencialmente

## Configuración de Spark

Los notebooks están configurados para ejecutarse en modo local por defecto. Para usar un cluster:

```python
spark = SparkSession.builder \
    .master("spark://master:7077") \
    .appName("MyApp") \
    .getOrCreate()
```

## MLflow Tracking

Para visualizar experimentos:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## Notas

- Cada notebook es independiente y puede ejecutarse por separado
- Los datos de ejemplo se generan automáticamente en cada notebook
- Los modelos se guardan en la carpeta `mlruns/`
- Los logs de Spark se almacenan en `logs/`

## Monitoreo con Grafana

El proyecto incluye dashboards pre-configurados de Grafana para monitorear:

### Dashboards Disponibles

1. **Fraud Detection Overview** (`fraud_overview`)
   - Transacciones en tiempo real
   - Métricas de fraude
   - Análisis por categoría y hora
   - Refresh: 5 segundos

2. **Model Performance Monitoring** (`model_performance`)
   - Métricas de modelos ML (accuracy, precision, recall, F1)
   - Confusion matrix components
   - Tendencias de performance
   - Refresh: 30 segundos

### Acceso a Grafana

```
URL: http://localhost:3000
Usuario: admin
Contraseña: admin
```

📖 Ver [GRAFANA_GUIDE.md](GRAFANA_GUIDE.md) para guía completa de uso

## Recursos Adicionales

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## Autor

Yusef González - Proyecto de aprendizaje Spark + MLflow
