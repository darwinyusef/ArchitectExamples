# Ejemplos Prácticos

Esta guía contiene ejemplos prácticos de uso para cada notebook y caso de uso común.

## 📚 Índice

1. [Ejecutar un Experimento Simple](#ejecutar-un-experimento-simple)
2. [Comparar Múltiples Modelos](#comparar-múltiples-modelos)
3. [Guardar y Cargar Modelos](#guardar-y-cargar-modelos)
4. [Consultas a PostgreSQL](#consultas-a-postgresql)
5. [Crear un DAG de Airflow](#crear-un-dag-de-airflow)
6. [Monitoreo y Debugging](#monitoreo-y-debugging)

---

## Ejecutar un Experimento Simple

### Con Spark ML + MLflow

```python
from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassifier
import mlflow
import mlflow.spark

# Iniciar Spark
spark = SparkSession.builder.appName("SimpleExperiment").getOrCreate()

# Configurar MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-first-experiment")

# Cargar datos (ejemplo)
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Entrenar con MLflow
with mlflow.start_run(run_name="rf-baseline"):
    # Log params
    mlflow.log_param("n_trees", 100)
    mlflow.log_param("max_depth", 10)

    # Entrenar
    rf = RandomForestClassifier(numTrees=100, maxDepth=10)
    model = rf.fit(df)

    # Evaluar y log metrics
    accuracy = evaluate_model(model, test_df)
    mlflow.log_metric("accuracy", accuracy)

    # Guardar modelo
    mlflow.spark.log_model(model, "random-forest")
```

---

## Comparar Múltiples Modelos

### Entrenar varios modelos y compararlos en MLflow UI

```python
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier
import mlflow

models = {
    "RandomForest": RandomForestClassifier(numTrees=100),
    "GBT": GBTClassifier(maxIter=100),
}

mlflow.set_experiment("model-comparison")

results = {}
for name, model in models.items():
    with mlflow.start_run(run_name=name):
        # Tag para filtrar
        mlflow.set_tag("model_family", name)

        # Entrenar
        fitted_model = model.fit(train_df)

        # Evaluar
        predictions = fitted_model.transform(test_df)
        accuracy = evaluator.evaluate(predictions)

        # Log
        mlflow.log_metric("accuracy", accuracy)
        mlflow.spark.log_model(fitted_model, f"{name.lower()}-model")

        results[name] = accuracy
        print(f"{name}: {accuracy:.4f}")

# Ver mejor modelo
best_model = max(results, key=results.get)
print(f"\nMejor modelo: {best_model} ({results[best_model]:.4f})")
```

Luego en MLflow UI (http://localhost:5000):
1. Navega al experimento "model-comparison"
2. Compara runs usando la tabla de métricas
3. Visualiza gráficos de comparación

---

## Guardar y Cargar Modelos

### Guardar modelo

```python
with mlflow.start_run() as run:
    # Entrenar modelo
    model = train_model(data)

    # Guardar en MLflow
    mlflow.spark.log_model(
        model,
        "production-model",
        registered_model_name="fraud-detector"
    )

    run_id = run.info.run_id
    print(f"Modelo guardado: runs:/{run_id}/production-model")
```

### Cargar modelo

```python
import mlflow.spark

# Opción 1: Cargar desde run_id
model = mlflow.spark.load_model(f"runs:/{run_id}/production-model")

# Opción 2: Cargar desde Model Registry
model = mlflow.spark.load_model("models:/fraud-detector/Production")

# Usar modelo
predictions = model.transform(new_data)
predictions.show()
```

---

## Consultas a PostgreSQL

### Conectar desde Python

```python
import pandas as pd
from sqlalchemy import create_engine

# Crear conexión
engine = create_engine(
    'postgresql://spark_user:spark_password@localhost:5432/spark_ml_db'
)

# Leer datos
df = pd.read_sql("SELECT * FROM customer_clusters LIMIT 10", engine)
print(df)

# Escribir datos
df_results.to_sql('my_table', engine, if_exists='replace', index=False)
```

### Conectar desde Spark

```python
# Leer con Spark JDBC
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/spark_ml_db") \
    .option("dbtable", "customer_clusters") \
    .option("user", "spark_user") \
    .option("password", "spark_password") \
    .load()

# Escribir con Spark
df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/spark_ml_db") \
    .option("dbtable", "predictions") \
    .option("user", "spark_user") \
    .option("password", "spark_password") \
    .mode("overwrite") \
    .save()
```

### Queries SQL Útiles

```sql
-- Ver distribución de clusters
SELECT cluster, COUNT(*) as num_customers
FROM customer_clusters
GROUP BY cluster
ORDER BY cluster;

-- Clientes de alto valor en cluster específico
SELECT customer_id, cluster, feature_0, feature_1
FROM customer_clusters
WHERE cluster = 2
  AND feature_0 > 100
ORDER BY feature_0 DESC
LIMIT 10;

-- Estadísticas por cluster
SELECT
    cluster,
    COUNT(*) as count,
    AVG(feature_0) as avg_feature_0,
    STDDEV(feature_0) as std_feature_0
FROM customer_clusters
GROUP BY cluster;
```

---

## Crear un DAG de Airflow

### Ejemplo básico

Crear archivo `airflow/dags/ml_pipeline.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'yusef',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_data():
    print("Extrayendo datos...")
    # Tu código aquí
    return "data_extracted"

def transform_data():
    print("Transformando datos...")
    # Tu código aquí
    return "data_transformed"

def train_model():
    print("Entrenando modelo...")
    # Tu código aquí
    return "model_trained"

with DAG(
    'ml_pipeline_daily',
    default_args=default_args,
    description='Pipeline ML diario',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )

    train = PythonOperator(
        task_id='train',
        python_callable=train_model,
    )

    # Definir dependencias
    extract >> transform >> train
```

Luego:
1. Guarda el archivo en `airflow/dags/`
2. Abre Airflow UI: http://localhost:8080
3. Activa el DAG
4. Trigger manual o espera el schedule

---

## Monitoreo y Debugging

### Ver logs de Spark

```python
# En tu código Spark
spark.sparkContext.setLogLevel("INFO")  # DEBUG, INFO, WARN, ERROR

# Logs personalizados
from py4j.java_gateway import java_import
java_import(spark._jvm, 'org.apache.log4j.Logger')
logger = spark._jvm.Logger.getLogger(__name__)
logger.info("Mi mensaje de log")
```

### Monitorear ejecución

```bash
# Ver logs de servicios
docker-compose logs -f mlflow
docker-compose logs -f postgres

# Ver logs de Spark en notebooks
# Spark UI generalmente en: http://localhost:4040
# (cuando hay una sesión activa)
```

### Debugging en MLflow

```python
# Buscar runs con ciertas características
from mlflow.tracking import MlflowClient

client = MlflowClient()
experiment = client.get_experiment_by_name("my-experiment")

# Filtrar runs
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="metrics.accuracy > 0.9",
    order_by=["metrics.accuracy DESC"],
    max_results=5
)

for run in runs:
    print(f"Run ID: {run.info.run_id}")
    print(f"Accuracy: {run.data.metrics['accuracy']}")
    print(f"Params: {run.data.params}")
    print()
```

### Debugging de PostgreSQL

```bash
# Conectar a PostgreSQL CLI
docker-compose exec postgres psql -U spark_user -d spark_ml_db

# Dentro del CLI
\dt                    # Listar tablas
\d customer_clusters   # Describir tabla
SELECT COUNT(*) FROM customer_clusters;
```

---

## Tips y Best Practices

### 1. Organizar Experimentos

```python
# Usar jerarquía de experimentos
mlflow.set_experiment("/production/fraud-detection")
mlflow.set_experiment("/development/fraud-detection")
mlflow.set_experiment("/research/new-algorithms")
```

### 2. Tags Útiles

```python
with mlflow.start_run():
    mlflow.set_tags({
        "team": "data-science",
        "project": "fraud-detection",
        "environment": "production",
        "version": "v1.2.3"
    })
```

### 3. Logging Completo

```python
with mlflow.start_run():
    # Params
    mlflow.log_params(all_hyperparameters)

    # Metrics por época
    for epoch in range(epochs):
        train_loss = train_epoch()
        mlflow.log_metric("train_loss", train_loss, step=epoch)

    # Artifacts
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("feature_importance.csv")

    # Modelo con signature
    from mlflow.models.signature import infer_signature
    signature = infer_signature(X_train, model.predict(X_train))
    mlflow.sklearn.log_model(model, "model", signature=signature)
```

### 4. Versionado de Datos

```python
# Log dataset info
with mlflow.start_run():
    mlflow.log_param("dataset_version", "v2.1")
    mlflow.log_param("dataset_size", len(df))
    mlflow.log_param("dataset_hash", hash_dataset(df))
```

---

## Recursos Adicionales

- **MLflow**: https://mlflow.org/docs/latest/tracking.html
- **Spark ML**: https://spark.apache.org/docs/latest/ml-guide.html
- **Airflow**: https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html
- **PostgreSQL**: https://www.postgresql.org/docs/

## Troubleshooting Común

### MLflow no guarda modelos

Verifica que el tracking URI esté configurado:
```python
print(mlflow.get_tracking_uri())  # Debe ser http://localhost:5000
```

### PostgreSQL connection refused

Espera 30 segundos más para inicialización:
```bash
docker-compose logs postgres | grep "ready to accept"
```

### Airflow DAG no aparece

1. Verifica que el archivo esté en `airflow/dags/`
2. Revisa errores: `docker-compose logs airflow-scheduler`
3. Refresca Airflow UI

---

¡Feliz aprendizaje! 🚀
