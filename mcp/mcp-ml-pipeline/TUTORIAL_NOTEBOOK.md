# 📓 Tutorial Interactivo: Spark + Airflow + MLflow

Notebook Jupyter completo que te guía paso a paso en el uso del pipeline de ML.

## 📋 Contenido del Notebook

### 1. Setup Inicial
- Verificación de servicios
- Instalación de dependencias
- Configuración de entorno

### 2. Introducción a Spark
- ¿Qué es Apache Spark?
- Arquitectura de Spark
- Crear SparkSession
- Spark UI

### 3. Procesamiento de Datos con Spark
- Crear dataset de ejemplo (10,000 registros de ventas)
- Convertir pandas → Spark DataFrame
- **Operaciones básicas**:
  - Filtrado
  - Agregaciones
  - Joins
  - Window Functions
- Análisis temporal con visualizaciones
- Guardar datos en Parquet

### 4. Entrenamiento de Modelos con Spark MLlib
- Preparación de features
- Feature engineering (indexing, vectorización, scaling)
- División train/test
- **Entrenar 2 modelos**:
  - Regresión Lineal
  - Random Forest
- Evaluación con métricas (RMSE, R², MAE)
- Comparación de modelos con gráficos

### 5. Tracking con MLflow
- Configurar MLflow
- Registrar experimentos
- Log de parámetros y métricas
- Guardar modelos
- Comparar experimentos en MLflow UI

### 6. Orquestación con Airflow
- Listar DAGs disponibles
- Disparar DAGs programáticamente
- Monitorear estado en tiempo real
- Código de ejemplo para DAG personalizado

### 7. Pipeline Completo End-to-End
- Función que integra todo:
  1. Carga de datos
  2. Procesamiento con Spark
  3. Entrenamiento de modelo
  4. Evaluación
  5. Registro en MLflow
- Ejecutar pipeline completo con un solo comando

### 8. Monitoreo y Debugging
- URLs de monitoreo
- Información de Spark Context
- Estadísticas de ejecución
- Cleanup de recursos

## 🚀 Cómo Usar el Notebook

### Opción 1: Jupyter Notebook

```bash
# 1. Asegúrate de que los servicios estén corriendo
cd mcp-ml-pipeline
docker-compose up -d

# 2. Esperar 2-3 minutos para inicialización
sleep 120

# 3. Instalar Jupyter
pip install jupyter notebook

# 4. Iniciar Jupyter
jupyter notebook

# 5. Abrir tutorial_spark_airflow.ipynb
```

### Opción 2: JupyterLab

```bash
# Instalar JupyterLab
pip install jupyterlab

# Iniciar
jupyter lab

# Navegar a tutorial_spark_airflow.ipynb
```

### Opción 3: VS Code

```bash
# 1. Instalar extensión de Jupyter en VS Code
# 2. Abrir tutorial_spark_airflow.ipynb
# 3. Seleccionar kernel de Python
# 4. Ejecutar celdas
```

## 📊 Requisitos

### Servicios (deben estar corriendo)

```bash
# Verificar que todos los servicios estén activos
docker-compose ps

# Deberías ver:
# - ml-postgres (PostgreSQL)
# - ml-mlflow (MLflow)
# - ml-airflow-webserver (Airflow Web)
# - ml-airflow-scheduler (Airflow Scheduler)
# - ml-spark-master (Spark Master)
# - ml-spark-worker (Spark Worker)
```

### Dependencias Python

El notebook instala automáticamente las dependencias, pero también puedes instalarlas manualmente:

```bash
pip install pyspark mlflow pandas numpy matplotlib seaborn scikit-learn jupyter
```

## 🎯 Flujo del Tutorial

```
┌─────────────────────────────────────────────────────┐
│              INICIO DEL TUTORIAL                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  1. Setup y Verificación de Servicios               │
│     ✓ Airflow, MLflow, Spark                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  2. Spark Basics                                    │
│     • Crear SparkSession                            │
│     • DataFrames                                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  3. Procesamiento de Datos                          │
│     • 10K registros de ventas                       │
│     • Filtros, Agregaciones, Joins                 │
│     • Window Functions                              │
│     • Análisis Temporal                             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  4. Machine Learning con MLlib                      │
│     • Feature Engineering                           │
│     • Train/Test Split                              │
│     • Regresión Lineal                             │
│     • Random Forest                                 │
│     • Evaluación y Comparación                     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  5. MLflow Tracking                                 │
│     • Log experimentos                              │
│     • Métricas: RMSE, R², MAE                      │
│     • Guardar modelos                               │
│     • Comparar en UI                                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  6. Airflow Orchestration                           │
│     • Listar DAGs                                   │
│     • Trigger DAGs                                  │
│     • Monitorear ejecución                          │
│     • Crear DAG personalizado                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  7. Pipeline End-to-End                             │
│     • Función que integra todo                      │
│     • Automatización completa                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  8. Monitoreo y Debugging                           │
│     • Spark UI, Airflow UI, MLflow UI              │
│     • Estadísticas de recursos                      │
│     • Cleanup                                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              ✅ TUTORIAL COMPLETADO                 │
└─────────────────────────────────────────────────────┘
```

## 📈 Resultados Esperados

Al completar el notebook, habrás:

### ✅ Procesado Datos
- 10,000 registros de ventas
- Análisis por categoría, región, tiempo
- Gráficos de tendencias

### ✅ Entrenado Modelos
- 2 modelos de ML (Linear Regression, Random Forest)
- Métricas de evaluación
- Comparación de rendimiento

### ✅ Registrado en MLflow
- 2+ experimentos
- Parámetros, métricas y modelos guardados
- Visible en http://localhost:5000

### ✅ Orquestado con Airflow
- DAG ejecutado
- Tareas monitoreadas
- Código de DAG personalizado

### ✅ Creado Pipeline Completo
- Función reutilizable
- Automatización end-to-end
- Listo para producción

## 🎓 Lo que Aprenderás

### Nivel Básico
- ✓ Conceptos de Spark (Driver, Executors, Partitions)
- ✓ DataFrames y operaciones básicas
- ✓ Leer/escribir datos en Parquet

### Nivel Intermedio
- ✓ Feature engineering con MLlib
- ✓ Entrenamiento de modelos
- ✓ Tracking de experimentos con MLflow
- ✓ Orquestación con Airflow

### Nivel Avanzado
- ✓ Window Functions
- ✓ Pipeline completo end-to-end
- ✓ Monitoreo y optimización
- ✓ Integración de múltiples herramientas

## 🔍 Visualizaciones Incluidas

El notebook genera gráficos automáticamente:

1. **Ventas por Mes**
   - Bar chart de totales
   - Line chart de ticket promedio

2. **Comparación de Modelos**
   - RMSE por modelo
   - MAE por modelo
   - R² por modelo

3. **Predicciones vs Real**
   - Tabla comparativa
   - Primeras 10 predicciones

## 🛠️ Personalización

### Cambiar Tamaño del Dataset

```python
# En la celda de creación de datos
n_records = 50000  # Cambiar de 10000 a 50000
```

### Cambiar Modelo de ML

```python
# En el pipeline completo
result = run_complete_pipeline(model_type='LinearRegression')
# o
result = run_complete_pipeline(model_type='RandomForest')
```

### Agregar Más Features

```python
# Modificar feature_cols
feature_cols = [
    'cantidad', 'precio_unitario', 'descuento',
    'mes', 'dia_semana', 'hora',
    'categoria_idx', 'region_idx',
    'nueva_feature_1',  # Agregar nueva
    'nueva_feature_2'   # Agregar nueva
]
```

### Cambiar Hiperparámetros

```python
# Random Forest
rf = RandomForestRegressor(
    numTrees=50,      # Cambiar de 20 a 50
    maxDepth=10,      # Cambiar de 5 a 10
    seed=42
)

# Linear Regression
lr = LinearRegression(
    maxIter=20,       # Cambiar de 10 a 20
    regParam=0.1      # Cambiar de 0.01 a 0.1
)
```

## 🐛 Troubleshooting

### Error: "Servicios no disponibles"

```bash
# Verificar que los servicios estén corriendo
docker-compose ps

# Si no están corriendo, iniciar
docker-compose up -d

# Esperar 2-3 minutos
sleep 120
```

### Error: "Spark Session not found"

```bash
# Reiniciar kernel de Jupyter
# Menu: Kernel → Restart Kernel

# Re-ejecutar celdas desde el inicio
```

### Error: "MLflow connection refused"

```bash
# Verificar que MLflow esté corriendo
curl http://localhost:5000/health

# Ver logs
docker-compose logs mlflow
```

### Error: "Airflow API 401 Unauthorized"

```bash
# Verificar credenciales en el código
AIRFLOW_AUTH = HTTPBasicAuth("airflow", "airflow")

# Verificar que Airflow esté corriendo
curl http://localhost:8080/health
```

### Jupyter se queda sin memoria

```bash
# Detener kernel
# Menu: Kernel → Restart & Clear Output

# Limpiar cache de Spark
train_data.unpersist()
test_data.unpersist()

# O reducir tamaño del dataset
n_records = 5000  # En lugar de 10000
```

## 📚 Recursos Adicionales

### Dentro del Notebook
- Código comentado en cada celda
- Explicaciones detalladas
- Links a documentación oficial

### Documentación Externa
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [MLlib Guide](https://spark.apache.org/docs/latest/ml-guide.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Airflow API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html)

### Ejemplos de Código
- DAG personalizado incluido
- Pipeline completo reutilizable
- Funciones de monitoreo

## 🎯 Próximos Pasos

Después de completar el tutorial:

1. **Experimenta**:
   - Modifica parámetros
   - Prueba otros modelos
   - Agrega más features

2. **Escala**:
   - Usa datasets más grandes
   - Conecta a cluster Spark real
   - Implementa en producción

3. **Optimiza**:
   - Tuning de hiperparámetros
   - Optimización de Spark
   - Paralelización avanzada

4. **Automatiza**:
   - Crea tus propios DAGs
   - Implementa CI/CD
   - Agrega alertas

## ⏱️ Tiempo Estimado

- **Setup**: 5 minutos
- **Ejecución completa**: 15-20 minutos
- **Con experimentación**: 1-2 horas

## 📝 Notas

- El notebook usa datos simulados (no requiere fuentes externas)
- Todas las dependencias se instalan automáticamente
- Compatible con Python 3.11+
- Requiere ~4GB RAM libre

---

**¡Disfruta aprendiendo Spark + Airflow + MLflow!** 🚀

Para preguntas o problemas, consulta el README principal del proyecto.
