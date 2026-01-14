"""
DAG de Airflow para el Sistema de Detección de Fraude

Este DAG orquesta el pipeline completo end-to-end:
1. Ingesta de datos desde PostgreSQL
2. Transformación y feature engineering con Spark
3. Predicción con modelo de MLflow
4. Almacenamiento de resultados en PostgreSQL

Autor: Yusef González
Versión: 1.0
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import os
import sys

# Agregar path del proyecto
sys.path.append('/Users/yusefgonzalez/proyectos/arquitecturas/spark')

# Configuración por defecto
default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['alerts@frauddetection.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Funciones del pipeline
def ingest_data(**context):
    """Task 1: Ingestar datos nuevos desde fuentes"""
    from pyspark.sql import SparkSession
    import mlflow

    print("⏳ Ingesta de datos...")

    # Inicializar Spark
    spark = SparkSession.builder \
        .appName("FraudDetection-Ingest") \
        .getOrCreate()

    # Leer de PostgreSQL (en producción, esto vendría de una API o stream)
    df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/spark_ml_db") \
        .option("dbtable", "transactions_raw") \
        .option("user", "spark_user") \
        .option("password", "spark_password") \
        .load()

    # Filtrar solo transacciones nuevas del último día
    from pyspark.sql.functions import col
    df_new = df.filter(
        col("timestamp") >= context['execution_date'] - timedelta(days=1)
    )

    count = df_new.count()
    print(f"✅ {count} transacciones nuevas ingestadas")

    # Guardar en Parquet
    output_path = f"/tmp/fraud_data_{context['ds']}.parquet"
    df_new.write.mode("overwrite").parquet(output_path)

    # Push a XCom para siguiente task
    context['ti'].xcom_push(key='data_path', value=output_path)
    context['ti'].xcom_push(key='record_count', value=count)

    spark.stop()
    return output_path


def transform_and_engineer_features(**context):
    """Task 2: Transformación y feature engineering"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, when
    from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer

    print("⏳ Transformación y feature engineering...")

    # Obtener path de datos
    data_path = context['ti'].xcom_pull(key='data_path', task_ids='ingest_data')

    spark = SparkSession.builder \
        .appName("FraudDetection-Transform") \
        .getOrCreate()

    # Leer datos
    df = spark.read.parquet(data_path)

    # Feature engineering
    df_featured = df \
        .withColumn('amount_log', col('amount').log1p()) \
        .withColumn('is_night', when(
            (col('transaction_hour') < 6) | (col('transaction_hour') > 22), 1
        ).otherwise(0)) \
        .withColumn('is_high_amount', when(col('amount') > 500, 1).otherwise(0)) \
        .withColumn('is_far', when(col('distance_from_home') > 50, 1).otherwise(0)) \
        .withColumn('risk_score',
                   col('is_international') * 0.25 +
                   col('is_night') * 0.20 +
                   col('is_high_amount') * 0.30 +
                   col('is_far') * 0.25)

    # Encoding
    indexer = StringIndexer(inputCol='merchant_category', outputCol='merchant_category_idx')
    df_featured = indexer.fit(df_featured).transform(df_featured)

    # Preparar features
    feature_cols = [
        'amount_log', 'merchant_category_idx', 'transaction_hour',
        'is_international', 'card_present', 'distance_from_home',
        'customer_age', 'num_transactions_day', 'is_night',
        'is_high_amount', 'is_far', 'risk_score'
    ]

    assembler = VectorAssembler(inputCols=feature_cols, outputCol='features_raw')
    df_assembled = assembler.transform(df_featured)

    scaler = StandardScaler(inputCol='features_raw', outputCol='features',
                           withMean=True, withStd=True)
    df_scaled = scaler.fit(df_assembled).transform(df_assembled)

    # Guardar
    output_path = f"/tmp/fraud_featured_{context['ds']}.parquet"
    df_scaled.write.mode("overwrite").parquet(output_path)

    print(f"✅ Features creadas: {len(feature_cols)}")

    context['ti'].xcom_push(key='featured_data_path', value=output_path)

    spark.stop()
    return output_path


def predict_fraud(**context):
    """Task 3: Predecir fraude usando modelo de MLflow"""
    from pyspark.sql import SparkSession
    import mlflow
    import mlflow.sklearn

    print("⏳ Prediciendo fraude...")

    # Cargar modelo desde MLflow
    mlflow.set_tracking_uri("http://localhost:5000")
    model_name = "fraud-detection-randomforest"
    model_stage = "Production"

    try:
        model_uri = f"models:/{model_name}/{model_stage}"
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Modelo cargado: {model_name} ({model_stage})")
    except Exception as e:
        print(f"⚠️  Error cargando modelo: {e}")
        print("   Usando modelo más reciente...")
        # Fallback: usar último modelo
        model_uri = f"models:/{model_name}/latest"
        model = mlflow.sklearn.load_model(model_uri)

    # Leer datos
    featured_path = context['ti'].xcom_pull(
        key='featured_data_path',
        task_ids='transform_and_engineer_features'
    )

    spark = SparkSession.builder \
        .appName("FraudDetection-Predict") \
        .getOrCreate()

    df = spark.read.parquet(featured_path)

    # Convertir a pandas para predicción
    df_pandas = df.toPandas()

    # Extraer features
    import numpy as np
    X = np.array([row.toArray() for row in df_pandas['features']])

    # Predecir
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    # Agregar predicciones
    df_pandas['predicted_fraud'] = predictions
    df_pandas['fraud_probability'] = probabilities
    df_pandas['prediction_date'] = datetime.now()
    df_pandas['model_name'] = model_name

    # Filtrar fraudes detectados
    df_frauds = df_pandas[df_pandas['predicted_fraud'] == 1]

    print(f"✅ {len(predictions)} transacciones procesadas")
    print(f"⚠️  {len(df_frauds)} fraudes detectados ({len(df_frauds)/len(predictions)*100:.2f}%)")

    # Guardar resultados
    output_path = f"/tmp/fraud_predictions_{context['ds']}.csv"
    df_pandas.to_csv(output_path, index=False)

    context['ti'].xcom_push(key='predictions_path', value=output_path)
    context['ti'].xcom_push(key='fraud_count', value=len(df_frauds))

    spark.stop()
    return output_path


def save_to_postgres(**context):
    """Task 4: Guardar predicciones en PostgreSQL"""
    import pandas as pd
    from sqlalchemy import create_engine

    print("⏳ Guardando en PostgreSQL...")

    # Leer predicciones
    predictions_path = context['ti'].xcom_pull(
        key='predictions_path',
        task_ids='predict_fraud'
    )

    df = pd.read_csv(predictions_path)

    # Conectar a PostgreSQL
    engine = create_engine(
        'postgresql://spark_user:spark_password@localhost:5432/spark_ml_db'
    )

    # Guardar
    df.to_sql(
        'fraud_predictions_daily',
        engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )

    print(f"✅ {len(df)} registros guardados en PostgreSQL")

    return True


def send_alert(**context):
    """Task 5: Enviar alertas si se detectan fraudes"""
    fraud_count = context['ti'].xcom_pull(key='fraud_count', task_ids='predict_fraud')
    total_count = context['ti'].xcom_pull(key='record_count', task_ids='ingest_data')

    print(f"\\n{'='*60}")
    print("RESUMEN DEL PIPELINE")
    print('='*60)
    print(f"Transacciones procesadas: {total_count}")
    print(f"Fraudes detectados: {fraud_count}")
    print(f"Tasa de fraude: {fraud_count/total_count*100:.2f}%")
    print('='*60)

    # En producción, enviar email/Slack/PagerDuty si fraud_count > threshold
    if fraud_count > 100:
        print(f"\\n⚠️  ALERTA: {fraud_count} fraudes detectados!")
        print("   Enviando notificación al equipo...")
        # send_email() o send_slack_notification()

    return True


# Definir DAG
with DAG(
    dag_id='fraud_detection_pipeline',
    default_args=default_args,
    description='Pipeline de detección de fraude end-to-end',
    schedule_interval='@daily',  # Ejecutar diariamente
    catchup=False,
    tags=['fraud-detection', 'ml', 'production'],
    max_active_runs=1,
) as dag:

    # Documentación del DAG
    dag.doc_md = """
    # Pipeline de Detección de Fraude

    Este DAG implementa el pipeline completo de ML para detectar fraudes:

    1. **Ingesta**: Lee transacciones nuevas
    2. **Transformación**: Feature engineering
    3. **Predicción**: Aplica modelo de MLflow
    4. **Persistencia**: Guarda en PostgreSQL
    5. **Alertas**: Notifica si hay fraudes

    ## Monitoreo
    - Revisar logs en caso de fallos
    - Validar métricas de modelo periódicamente
    - Actualizar modelo si performance degrada
    """

    # Definir tasks
    task_ingest = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data,
        provide_context=True,
    )

    task_transform = PythonOperator(
        task_id='transform_and_engineer_features',
        python_callable=transform_and_engineer_features,
        provide_context=True,
    )

    task_predict = PythonOperator(
        task_id='predict_fraud',
        python_callable=predict_fraud,
        provide_context=True,
    )

    task_save = PythonOperator(
        task_id='save_to_postgres',
        python_callable=save_to_postgres,
        provide_context=True,
    )

    task_alert = PythonOperator(
        task_id='send_alert',
        python_callable=send_alert,
        provide_context=True,
        trigger_rule='all_done',  # Ejecutar siempre
    )

    # Definir dependencias
    task_ingest >> task_transform >> task_predict >> task_save >> task_alert
