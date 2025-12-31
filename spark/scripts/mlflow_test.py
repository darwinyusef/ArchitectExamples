#!/usr/bin/env python3
"""Script de prueba rápido para MLflow.

Registra parámetros, métricas y un artefacto en un tracking store local
`mlruns_test/` en la raíz del proyecto.
"""
import os
import time
import mlflow


def main():
    # Usar un tracking store local separado para pruebas
    tracking_dir = os.path.abspath(os.path.join(os.getcwd(), "mlruns_test"))
    mlflow.set_tracking_uri(f"file://{tracking_dir}")

    experiment_name = "mlflow_quick_test"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        print(f"Run ID: {run.info.run_id}")
        mlflow.log_param("test_param", "quick_check")
        mlflow.log_param("timestamp", int(time.time()))

        # Log metrics progresivamente
        for step in range(5):
            metric_val = 0.5 + step * 0.1
            mlflow.log_metric("accuracy", metric_val, step=step)
            print(f"Logged metric accuracy={metric_val} (step={step})")
            time.sleep(0.1)

        # Crear y registrar un artefacto simple
        artifact_dir = os.path.join(os.getcwd(), "scripts", "artifacts")
        os.makedirs(artifact_dir, exist_ok=True)
        artifact_path = os.path.join(artifact_dir, "hello.txt")
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write("Hola desde MLflow test.\n")

        mlflow.log_artifact(artifact_path, artifact_path="examples")
        print(f"Logged artifact: {artifact_path}")

        print("Artifact URI:", mlflow.get_artifact_uri())


if __name__ == "__main__":
    main()
