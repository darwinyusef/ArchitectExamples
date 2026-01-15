import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import mlflow
import mlflow.sklearn
from prefect import task, flow
from typing import Tuple, Dict
import os


# --- CONFIGURACIÓN DE CONSTANTES ---
COSTO_KWH_EPM = 765.37
MARGEN_MERCADO = 1.3
MODELO_ONNX_PATH = "costos_cajas_laser.onnx"

# Data Definition
@task(name="Definir especificaciones de productos")
def definir_productos() -> Dict:
    """Define las especificaciones de los productos de cajas láser."""
    specs = {
        'Caja 1 (Pequeña)': [360, 24, 0.025],
        'Caja 2 (Mediana)': [240, 26, 0.016],
        'Caja 3 (Grande)': [300, 48, 0.020]
    }
    return specs

# Data Generation
@task(name="Generar datos de entrenamiento")
def generar_datos_entrenamiento(specs: Dict, costo_kwh: float) -> pd.DataFrame:
    """
    Genera datos de entrenamiento simulando 3 meses de operación.

    Args:
        specs: Diccionario con especificaciones de productos
        costo_kwh: Costo por kWh de energía

    Returns:
        DataFrame con datos de entrenamiento
    """
    data = []
    for mes in [1, 2, 3]:
        for producto, valores in specs.items():
            # Añadimos un ligero ruido para simular variaciones reales
            costo_base = (
                (valores[0] * 0.025) +
                (valores[1] * 0.15 * (1.05**mes)) +
                (valores[2] * costo_kwh)
            )
            data.append(valores + [costo_base])

    df = pd.DataFrame(
        data,
        columns=['tiempo_seg', 'material_cm2', 'energia_kwh', 'costo_real']
    )

    print(f"✅ Datos generados: {len(df)} registros")
    return df

# Data Preparation
@task(name="Preparar datos para entrenamiento")
def preparar_datos(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Separa features (X) y target (y) del DataFrame.

    Args:
        df: DataFrame con los datos

    Returns:
        Tupla con (X, y)
    """
    X = df[['tiempo_seg', 'material_cm2', 'energia_kwh']].values
    y = df['costo_real'].values

    print(f"✅ Datos preparados - Shape X: {X.shape}, Shape y: {y.shape}")
    return X, y

# Train Model
@task(name="Entrenar modelo de regresión")
def entrenar_modelo(X: np.ndarray, y: np.ndarray) -> LinearRegression:
    """
    Entrena el modelo de regresión lineal múltiple.

    Args:
        X: Features de entrenamiento
        y: Target de entrenamiento

    Returns:
        Modelo entrenado
    """
    modelo = LinearRegression()
    modelo.fit(X, y)

    print(f"✅ Modelo entrenado")
    print(f"   Coeficientes: {modelo.coef_}")
    print(f"   Intercepto: {modelo.intercept_:.2f}")

    return modelo

# Evaluate Model
@task(name="Evaluar modelo")
def evaluar_modelo(
    modelo: LinearRegression,
    X: np.ndarray,
    y: np.ndarray
) -> Dict[str, float]:
    """
    Evalúa el modelo y retorna métricas de rendimiento.

    Args:
        modelo: Modelo entrenado
        X: Features de evaluación
        y: Target de evaluación

    Returns:
        Diccionario con métricas
    """
    y_pred = modelo.predict(X)

    metricas = {
        'r2_score': r2_score(y, y_pred),
        'mse': mean_squared_error(y, y_pred),
        'rmse': np.sqrt(mean_squared_error(y, y_pred)),
        'mae': mean_absolute_error(y, y_pred)
    }

    print("\n--- MÉTRICAS DEL MODELO A NIVEL DE OUTLIERS ---")
    print(f"  R² Score (Coeficiente de Determinación): {metricas['r2_score']:.4f}")
    print(f"  MSE (Error Cuadrático Medio): {metricas['mse']:.2f}")
    print(f"  RMSE (Raíz del Error Cuadrático Medio): {metricas['rmse']:.2f}")
    print(f"  MAE (Error Absoluto Medio): {metricas['mae']:.2f}")

    return metricas

# Evaluate Model
@task(name="Generar predicciones por producto")
def generar_predicciones(
    modelo: LinearRegression,
    specs: Dict,
    margen: float
) -> pd.DataFrame:
    """
    Genera predicciones de costo y precio para cada producto.

    Args:
        modelo: Modelo entrenado
        specs: Especificaciones de productos
        margen: Margen de mercado a aplicar

    Returns:
        DataFrame con predicciones
    """
    resultados = []

    print("\n--- PREDICCIONES POR PRODUCTO ---")
    for nombre, valores in specs.items():
        prediccion = modelo.predict([valores])[0]
        precio_detal = prediccion * margen

        resultados.append({
            'producto': nombre,
            'costo_produccion': prediccion,
            'precio_detal': precio_detal,
            'tiempo_seg': valores[0],
            'material_cm2': valores[1],
            'energia_kwh': valores[2]
        })

        print(f"📦 {nombre}:")
        print(f"   Costo Producción: ${prediccion:.2f} COP")
        print(f"   Precio al Detal: ${precio_detal:.2f} COP")

    return pd.DataFrame(resultados)

# Export to ONNX
@task(name="Exportar modelo a ONNX")
def exportar_a_onnx(
    modelo: LinearRegression,
    output_path: str
) -> str:
    """
    Exporta el modelo entrenado a formato ONNX.

    Args:
        modelo: Modelo entrenado
        output_path: Ruta del archivo ONNX de salida

    Returns:
        Ruta del archivo generado
    """
    initial_type = [('float_input', FloatTensorType([None, 3]))]
    onx = convert_sklearn(modelo, initial_types=initial_type)

    with open(output_path, "wb") as f:
        f.write(onx.SerializeToString())

    print(f"\n✅ Modelo exportado a ONNX: {output_path}")
    return output_path


@task(name="Registrar en MLflow")
def registrar_en_mlflow(
    modelo: LinearRegression,
    metricas: Dict[str, float],
    params: Dict,
    predicciones: pd.DataFrame,
    onnx_path: str
) -> str:
    """
    Registra el modelo, métricas y artifacts en MLflow.

    Args:
        modelo: Modelo entrenado
        metricas: Diccionario con métricas de evaluación
        params: Diccionario con parámetros del modelo
        predicciones: DataFrame con predicciones
        onnx_path: Ruta del archivo ONNX

    Returns:
        Run ID de MLflow
    """
    with mlflow.start_run() as run:
        # Log de parámetros
        mlflow.log_params(params)

        # Log de métricas
        mlflow.log_metrics(metricas)

        # Log del modelo sklearn
        mlflow.sklearn.log_model(
            modelo,
            "modelo_regresion_laser",
            registered_model_name="CostosLaser"
        )

        # Log de artifacts
        mlflow.log_artifact(onnx_path, "onnx_model")

        # Guardar predicciones como CSV y hacer log
        pred_path = "predicciones.csv"
        predicciones.to_csv(pred_path, index=False)
        mlflow.log_artifact(pred_path, "predicciones")

        # Log de coeficientes del modelo
        mlflow.log_param("coeficientes", str(modelo.coef_))
        mlflow.log_param("intercepto", float(modelo.intercept_))

        print(f"\n✅ Modelo registrado en MLflow - Run ID: {run.info.run_id}")

        # Limpiar archivo temporal
        if os.path.exists(pred_path):
            os.remove(pred_path)

        return run.info.run_id


@flow(name="Pipeline de Modelo de Costos Láser")
def pipeline_modelo_laser():
    """
    Flujo principal que orquesta todo el pipeline de entrenamiento,
    evaluación y registro del modelo de costos de corte láser.
    """
    print("=" * 60)
    print("INICIANDO PIPELINE DE MODELO DE COSTOS LÁSER")
    print("=" * 60)

    # Configurar MLflow
    mlflow.set_experiment("Modelo_Costos_Laser_Antioquia")

    # 1. Definir productos y especificaciones
    specs = definir_productos()

    # 2. Generar datos de entrenamiento
    df = generar_datos_entrenamiento(specs, COSTO_KWH_EPM)

    # 3. Preparar datos
    X, y = preparar_datos(df)

    # 4. Entrenar modelo
    modelo = entrenar_modelo(X, y)

    # 5. Evaluar modelo
    metricas = evaluar_modelo(modelo, X, y)

    # 6. Generar predicciones
    predicciones = generar_predicciones(modelo, specs, MARGEN_MERCADO)

    # 7. Exportar a ONNX
    onnx_path = exportar_a_onnx(modelo, MODELO_ONNX_PATH)

    # 8. Registrar en MLflow
    params = {
        'costo_kwh_epm': COSTO_KWH_EPM,
        'margen_mercado': MARGEN_MERCADO,
        'n_meses': 3,
        'n_productos': len(specs),
        'n_features': 3
    }

    run_id = registrar_en_mlflow(
        modelo,
        metricas,
        params,
        predicciones,
        onnx_path
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"MLflow Run ID: {run_id}")
    print(f"Modelo ONNX: {onnx_path}")
    print(f"R² Score: {metricas['r2_score']:.4f}")

    return {
        'run_id': run_id,
        'metricas': metricas,
        'predicciones': predicciones
    }


if __name__ == "__main__":
    # Ejecutar el pipeline
    resultado = pipeline_modelo_laser()