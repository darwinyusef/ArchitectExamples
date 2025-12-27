"""
MCP Server para ML Pipeline con Spark, MLflow y Airflow
Incluye WebSockets para monitoreo en tiempo real
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import asyncio

# Importaciones para Spark
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import RegressionEvaluator

# Importaciones para MLflow
import mlflow
import mlflow.spark
from mlflow.tracking import MlflowClient

# Importaciones para Airflow (API REST)
import requests
from requests.auth import HTTPBasicAuth

# Crear servidor MCP
mcp = FastMCP("ML-Pipeline")

# Configuración
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL", "http://localhost:8080/api/v1")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

# Configurar MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Estado global para WebSocket
pipeline_status = {
    "current_step": None,
    "progress": 0,
    "logs": [],
    "last_update": None
}


def get_spark_session():
    """Obtiene o crea una sesión de Spark"""
    return SparkSession.builder \
        .appName("MCP-ML-Pipeline") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()


def log_pipeline_event(step: str, message: str, level: str = "INFO"):
    """Registra eventos del pipeline para WebSocket"""
    global pipeline_status
    event = {
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "message": message,
        "level": level
    }
    pipeline_status["logs"].append(event)
    pipeline_status["current_step"] = step
    pipeline_status["last_update"] = datetime.now().isoformat()

    # Mantener solo los últimos 100 logs
    if len(pipeline_status["logs"]) > 100:
        pipeline_status["logs"] = pipeline_status["logs"][-100:]


@mcp.tool()
def train_model(
    data_path: str,
    features: List[str],
    target: str,
    experiment_name: str = "default",
    model_name: str = "linear_regression"
) -> Dict[str, Any]:
    """
    Entrena un modelo de Machine Learning con Spark y lo registra en MLflow.

    Args:
        data_path: Ruta al archivo de datos (CSV, Parquet, etc.)
        features: Lista de columnas a usar como features
        target: Columna objetivo
        experiment_name: Nombre del experimento en MLflow
        model_name: Nombre del modelo a entrenar

    Returns:
        Resultados del entrenamiento y métricas
    """
    try:
        log_pipeline_event("training", f"Iniciando entrenamiento de modelo {model_name}", "INFO")

        # Crear o usar experimento existente
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Obtener sesión de Spark
            spark = get_spark_session()
            log_pipeline_event("training", "Sesión de Spark iniciada", "INFO")

            # Cargar datos
            log_pipeline_event("training", f"Cargando datos desde {data_path}", "INFO")
            if data_path.endswith('.csv'):
                df = spark.read.csv(data_path, header=True, inferSchema=True)
            elif data_path.endswith('.parquet'):
                df = spark.read.parquet(data_path)
            else:
                raise ValueError("Formato de archivo no soportado. Usa CSV o Parquet")

            # Preparar features
            assembler = VectorAssembler(inputCols=features, outputCol="features")
            data = assembler.transform(df)

            # Dividir datos
            train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)
            log_pipeline_event("training", f"Datos divididos: {train_data.count()} train, {test_data.count()} test", "INFO")

            # Entrenar modelo
            log_pipeline_event("training", "Entrenando modelo...", "INFO")
            lr = LinearRegression(featuresCol="features", labelCol=target)
            model = lr.fit(train_data)

            # Evaluar modelo
            predictions = model.transform(test_data)
            evaluator = RegressionEvaluator(labelCol=target, predictionCol="prediction")

            rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
            r2 = evaluator.evaluate(predictions, {evaluator.metricName: "r2"})
            mae = evaluator.evaluate(predictions, {evaluator.metricName: "mae"})

            log_pipeline_event("training", f"Métricas - RMSE: {rmse:.4f}, R2: {r2:.4f}, MAE: {mae:.4f}", "INFO")

            # Registrar en MLflow
            mlflow.log_param("features", features)
            mlflow.log_param("target", target)
            mlflow.log_param("model_type", model_name)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("mae", mae)

            # Guardar modelo
            mlflow.spark.log_model(model, "model")

            run_id = mlflow.active_run().info.run_id
            log_pipeline_event("training", f"Modelo registrado con run_id: {run_id}", "SUCCESS")

            return {
                "success": True,
                "run_id": run_id,
                "metrics": {
                    "rmse": rmse,
                    "r2": r2,
                    "mae": mae
                },
                "model_uri": f"runs:/{run_id}/model",
                "experiment_name": experiment_name
            }

    except Exception as e:
        log_pipeline_event("training", f"Error: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@mcp.tool()
def list_experiments() -> Dict[str, Any]:
    """
    Lista todos los experimentos en MLflow.

    Returns:
        Lista de experimentos con sus metadatos
    """
    try:
        client = MlflowClient()
        experiments = client.search_experiments()

        result = []
        for exp in experiments:
            result.append({
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location,
                "lifecycle_stage": exp.lifecycle_stage,
                "tags": exp.tags
            })

        return {
            "success": True,
            "experiments": result,
            "total": len(result)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_experiment_runs(experiment_name: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Obtiene los runs de un experimento específico.

    Args:
        experiment_name: Nombre del experimento
        max_results: Número máximo de runs a retornar

    Returns:
        Lista de runs con sus métricas
    """
    try:
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)

        if not experiment:
            return {
                "success": False,
                "error": f"Experimento '{experiment_name}' no encontrado"
            }

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=max_results,
            order_by=["start_time DESC"]
        )

        result = []
        for run in runs:
            result.append({
                "run_id": run.info.run_id,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "status": run.info.status,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "tags": run.data.tags
            })

        return {
            "success": True,
            "experiment_name": experiment_name,
            "runs": result,
            "total": len(result)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def compare_models(experiment_name: str, metric: str = "rmse") -> Dict[str, Any]:
    """
    Compara modelos de un experimento basado en una métrica.

    Args:
        experiment_name: Nombre del experimento
        metric: Métrica para comparar (rmse, r2, mae, etc.)

    Returns:
        Comparación de modelos ordenados por la métrica
    """
    try:
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)

        if not experiment:
            return {
                "success": False,
                "error": f"Experimento '{experiment_name}' no encontrado"
            }

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="",
            order_by=[f"metrics.{metric} ASC"]
        )

        comparison = []
        for run in runs:
            if metric in run.data.metrics:
                comparison.append({
                    "run_id": run.info.run_id,
                    "start_time": datetime.fromtimestamp(run.info.start_time/1000).isoformat(),
                    metric: run.data.metrics[metric],
                    "params": run.data.params,
                    "all_metrics": run.data.metrics
                })

        return {
            "success": True,
            "experiment_name": experiment_name,
            "compared_by": metric,
            "models": comparison,
            "best_model": comparison[0] if comparison else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def trigger_airflow_dag(dag_id: str, conf: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Dispara un DAG de Airflow.

    Args:
        dag_id: ID del DAG a ejecutar
        conf: Configuración opcional para el DAG

    Returns:
        Información de la ejecución del DAG
    """
    try:
        log_pipeline_event("airflow", f"Disparando DAG: {dag_id}", "INFO")

        url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

        payload = {
            "conf": conf or {}
        }

        response = requests.post(url, json=payload, headers=headers, auth=auth)
        response.raise_for_status()

        result = response.json()
        log_pipeline_event("airflow", f"DAG disparado exitosamente: {result.get('dag_run_id')}", "SUCCESS")

        return {
            "success": True,
            "dag_run_id": result.get("dag_run_id"),
            "execution_date": result.get("execution_date"),
            "state": result.get("state")
        }
    except Exception as e:
        log_pipeline_event("airflow", f"Error al disparar DAG: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_dag_status(dag_id: str, dag_run_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene el estado de un DAG de Airflow.

    Args:
        dag_id: ID del DAG
        dag_run_id: ID del run específico (opcional, usa el último si no se especifica)

    Returns:
        Estado del DAG y sus tareas
    """
    try:
        if dag_run_id:
            url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}"
        else:
            # Obtener el último run
            url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"

        auth = HTTPBasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        response = requests.get(url, auth=auth)
        response.raise_for_status()

        result = response.json()

        if not dag_run_id:
            # Tomar el run más reciente
            runs = result.get("dag_runs", [])
            if not runs:
                return {
                    "success": False,
                    "error": "No se encontraron runs para este DAG"
                }
            result = runs[0]

        # Obtener estado de las tareas
        tasks_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{result['dag_run_id']}/taskInstances"
        tasks_response = requests.get(tasks_url, auth=auth)
        tasks = tasks_response.json().get("task_instances", []) if tasks_response.ok else []

        return {
            "success": True,
            "dag_id": dag_id,
            "dag_run_id": result.get("dag_run_id"),
            "state": result.get("state"),
            "start_date": result.get("start_date"),
            "end_date": result.get("end_date"),
            "tasks": [{
                "task_id": t.get("task_id"),
                "state": t.get("state"),
                "start_date": t.get("start_date"),
                "end_date": t.get("end_date"),
                "duration": t.get("duration")
            } for t in tasks]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_airflow_dags() -> Dict[str, Any]:
    """
    Lista todos los DAGs disponibles en Airflow.

    Returns:
        Lista de DAGs con sus metadatos
    """
    try:
        url = f"{AIRFLOW_API_URL}/dags"
        auth = HTTPBasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

        response = requests.get(url, auth=auth)
        response.raise_for_status()

        result = response.json()
        dags = result.get("dags", [])

        return {
            "success": True,
            "dags": [{
                "dag_id": dag.get("dag_id"),
                "is_active": dag.get("is_active"),
                "is_paused": dag.get("is_paused"),
                "schedule_interval": dag.get("schedule_interval"),
                "tags": dag.get("tags", [])
            } for dag in dags],
            "total": len(dags)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_pipeline_status() -> Dict[str, Any]:
    """
    Obtiene el estado actual del pipeline (para WebSocket monitoring).

    Returns:
        Estado actual del pipeline con logs recientes
    """
    global pipeline_status
    return {
        "success": True,
        "status": pipeline_status,
        "active": pipeline_status["current_step"] is not None
    }


@mcp.tool()
def process_spark_data(
    input_path: str,
    output_path: str,
    transformation: str = "filter"
) -> Dict[str, Any]:
    """
    Procesa datos con Spark y guarda el resultado.

    Args:
        input_path: Ruta de entrada de datos
        output_path: Ruta de salida de datos procesados
        transformation: Tipo de transformación (filter, aggregate, join)

    Returns:
        Resultado del procesamiento
    """
    try:
        log_pipeline_event("spark", f"Procesando datos: {input_path}", "INFO")

        spark = get_spark_session()

        # Cargar datos
        if input_path.endswith('.csv'):
            df = spark.read.csv(input_path, header=True, inferSchema=True)
        elif input_path.endswith('.parquet'):
            df = spark.read.parquet(input_path)
        else:
            raise ValueError("Formato no soportado")

        initial_count = df.count()
        log_pipeline_event("spark", f"Registros cargados: {initial_count}", "INFO")

        # Ejemplo de transformación (personalizar según necesidad)
        if transformation == "filter":
            # Filtrar valores nulos
            processed_df = df.na.drop()
        elif transformation == "aggregate":
            # Ejemplo de agregación
            processed_df = df.groupBy(df.columns[0]).count()
        else:
            processed_df = df

        final_count = processed_df.count()

        # Guardar resultado
        processed_df.write.mode("overwrite").parquet(output_path)
        log_pipeline_event("spark", f"Datos procesados guardados en {output_path}", "SUCCESS")

        return {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "transformation": transformation,
            "initial_records": initial_count,
            "final_records": final_count
        }
    except Exception as e:
        log_pipeline_event("spark", f"Error: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.resource("pipeline://status")
def get_status_resource() -> str:
    """Resource que provee el estado del pipeline"""
    status = get_pipeline_status()
    return json.dumps(status, indent=2)


@mcp.resource("mlflow://experiments")
def get_experiments_resource() -> str:
    """Resource que provee la lista de experimentos"""
    experiments = list_experiments()
    return json.dumps(experiments, indent=2)


if __name__ == "__main__":
    mcp.run()
