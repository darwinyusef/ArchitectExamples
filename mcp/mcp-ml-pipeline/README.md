# MCP ML Pipeline con Spark, MLflow y Airflow

Servidor MCP para orquestar pipelines de Machine Learning usando Spark para procesamiento, MLflow para tracking de experimentos y Airflow para orquestación. Incluye monitoreo en tiempo real mediante WebSockets.

## Arquitectura

```
┌─────────────┐
│   Airflow   │ ← Orquestación de pipelines
└──────┬──────┘
       │
       ├─→ ┌─────────┐
       │   │  Spark  │ ← Procesamiento de datos y entrenamiento
       │   └─────────┘
       │
       └─→ ┌─────────┐
           │ MLflow  │ ← Tracking y registro de modelos
           └─────────┘
```

## Características

- ✅ Entrenamiento de modelos con Spark MLlib
- ✅ Tracking de experimentos con MLflow
- ✅ Comparación y versionado de modelos
- ✅ Orquestación de pipelines con Airflow
- ✅ Monitoreo en tiempo real (WebSockets)
- ✅ Procesamiento distribuido de datos
- ✅ API REST completa

## Instalación

### 1. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar servicios con Docker

```bash
# Crear directorios necesarios
mkdir -p airflow/dags airflow/logs airflow/plugins

# Dar permisos al script de inicialización
chmod +x init-db.sh

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 3. Verificar servicios

```bash
# Airflow: http://localhost:8080
# Usuario: airflow / Contraseña: airflow

# MLflow: http://localhost:5000

# Spark Master: http://localhost:8081
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

## Uso

### Iniciar el servidor MCP

```bash
python server.py
```

### 📓 Tutorial Interactivo con Jupyter Notebook

Incluimos un **notebook completo** que te guía paso a paso:

```bash
# Instalar Jupyter
pip install jupyter notebook

# Iniciar Jupyter
jupyter notebook

# Abrir: tutorial_spark_airflow.ipynb
```

El notebook cubre:
- ✅ Spark fundamentals (DataFrames, operaciones, Window Functions)
- ✅ Procesamiento de 10K registros de ventas simulados
- ✅ Entrenamiento de modelos ML (Linear Regression, Random Forest)
- ✅ Tracking con MLflow
- ✅ Orquestación con Airflow
- ✅ Pipeline completo end-to-end
- ✅ Monitoreo y debugging

**Ver**: [TUTORIAL_NOTEBOOK.md](./TUTORIAL_NOTEBOOK.md) para más detalles.

### Herramientas disponibles

#### 1. `train_model`
Entrena un modelo con Spark y lo registra en MLflow:
```python
train_model(
    data_path="/path/to/data.csv",
    features=["feature1", "feature2", "feature3"],
    target="target_column",
    experiment_name="my_experiment",
    model_name="linear_regression"
)
```

#### 2. `process_spark_data`
Procesa datos con Spark:
```python
process_spark_data(
    input_path="/data/raw.csv",
    output_path="/data/processed.parquet",
    transformation="filter"
)
```

#### 3. `list_experiments`
Lista todos los experimentos de MLflow:
```python
list_experiments()
```

#### 4. `get_experiment_runs`
Obtiene los runs de un experimento:
```python
get_experiment_runs(
    experiment_name="my_experiment",
    max_results=10
)
```

#### 5. `compare_models`
Compara modelos basándose en métricas:
```python
compare_models(
    experiment_name="my_experiment",
    metric="rmse"
)
```

#### 6. `trigger_airflow_dag`
Dispara un DAG de Airflow:
```python
trigger_airflow_dag(
    dag_id="ml_pipeline",
    conf={"param1": "value1"}
)
```

#### 7. `get_dag_status`
Obtiene el estado de un DAG:
```python
get_dag_status(
    dag_id="ml_pipeline",
    dag_run_id="manual__2024-01-01T00:00:00+00:00"
)
```

#### 8. `list_airflow_dags`
Lista todos los DAGs disponibles:
```python
list_airflow_dags()
```

#### 9. `get_pipeline_status`
Obtiene el estado en tiempo real del pipeline:
```python
get_pipeline_status()
```

## Ejemplo de uso con LLM

El LLM puede interactuar naturalmente con el pipeline:

- "Entrena un modelo de regresión lineal con los datos en /data/sales.csv usando las columnas price, quantity y discount para predecir revenue"
- "Compara todos los modelos del experimento 'sales_prediction' usando RMSE"
- "Dispara el pipeline de ML y monitorea su progreso"
- "¿Cuál es el mejor modelo basado en R²?"
- "Lista todos los experimentos y muéstrame el más reciente"

## DAG de ejemplo

El archivo `airflow/dags/ml_pipeline_dag.py` contiene un DAG de ejemplo que:

1. Verifica la calidad de los datos
2. Preprocesa los datos con Spark
3. Entrena el modelo
4. Registra el modelo en MLflow
5. Valida el modelo
6. Notifica la finalización

## Monitoreo en tiempo real

El servidor mantiene un estado global del pipeline que se puede consultar:

```python
status = get_pipeline_status()
# Retorna:
# {
#   "current_step": "training",
#   "progress": 75,
#   "logs": [...],
#   "last_update": "2024-01-01T12:00:00"
# }
```

## Estructura de datos para entrenamiento

Ejemplo de CSV para entrenamiento:

```csv
feature1,feature2,feature3,target
10,20,30,100
15,25,35,125
20,30,40,150
```

## Comandos útiles

### Docker

```bash
# Ver estado de servicios
docker-compose ps

# Reiniciar un servicio
docker-compose restart mlflow

# Ver logs de un servicio específico
docker-compose logs -f spark-master

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Airflow CLI

```bash
# Ejecutar comando en el contenedor de Airflow
docker exec -it ml-airflow-webserver bash

# Listar DAGs
docker exec ml-airflow-webserver airflow dags list

# Disparar un DAG manualmente
docker exec ml-airflow-webserver airflow dags trigger ml_pipeline

# Ver tareas de un DAG
docker exec ml-airflow-webserver airflow tasks list ml_pipeline
```

### Spark

```bash
# Acceder al Spark Master
docker exec -it ml-spark-master bash

# Ejecutar spark-submit
docker exec ml-spark-master spark-submit --master spark://spark-master:7077 /path/to/script.py
```

## Troubleshooting

### Airflow no inicia
```bash
# Verificar base de datos
docker-compose logs postgres

# Reinicializar base de datos de Airflow
docker exec ml-airflow-webserver airflow db reset
```

### MLflow no registra modelos
```bash
# Verificar conexión a PostgreSQL
docker exec ml-mlflow curl -f http://localhost:5000/health

# Revisar logs
docker-compose logs mlflow
```

### Spark no procesa datos
```bash
# Verificar conectividad master-worker
docker-compose logs spark-worker

# Reiniciar cluster de Spark
docker-compose restart spark-master spark-worker
```

## Seguridad

⚠️ **IMPORTANTE**: Esta configuración es para desarrollo. Para producción:

- Cambiar credenciales por defecto
- Configurar autenticación robusta
- Usar HTTPS/TLS
- Implementar control de acceso basado en roles
- Aislar redes de Docker
- Configurar límites de recursos

## Extensiones

### Agregar más transformaciones de Spark

Edita la función `process_spark_data` en `server.py` para agregar transformaciones personalizadas.

### Crear nuevos DAGs

Agrega archivos Python en `airflow/dags/` siguiendo el patrón de `ml_pipeline_dag.py`.

### Integrar otros frameworks ML

Puedes agregar soporte para TensorFlow, PyTorch, XGBoost, etc. modificando la función `train_model`.

## Referencias

- [Apache Spark](https://spark.apache.org/)
- [MLflow](https://mlflow.org/)
- [Apache Airflow](https://airflow.apache.org/)
- [FastMCP](https://github.com/jlowin/fastmcp)
