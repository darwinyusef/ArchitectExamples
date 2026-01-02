
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'yusef',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['yusef@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'spark_ml_pipeline',
    default_args=default_args,
    description='Pipeline ML con Spark y MLflow',
    schedule_interval='@daily',  # Ejecutar diariamente
    catchup=False,
    tags=['spark', 'ml', 'mlflow'],
)

# Task 1: Ingesta
ingest_task = SparkSubmitOperator(
    task_id='ingest_data',
    application='scripts/ingest_data.py',
    conn_id='spark_default',
    dag=dag,
)

# Task 2: Transformación
transform_task = SparkSubmitOperator(
    task_id='transform_data',
    application='scripts/transform_data.py',
    conn_id='spark_default',
    dag=dag,
)

# Task 3: Feature Engineering
feature_task = SparkSubmitOperator(
    task_id='feature_engineering',
    application='scripts/feature_engineering.py',
    conn_id='spark_default',
    dag=dag,
)

# Task 4: Training
train_task = SparkSubmitOperator(
    task_id='train_model',
    application='scripts/train_model.py',
    conn_id='spark_default',
    dag=dag,
)

# Task 5: Evaluation
eval_task = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model_func,
    dag=dag,
)

# Definir dependencias
ingest_task >> transform_task >> feature_task >> train_task >> eval_task
