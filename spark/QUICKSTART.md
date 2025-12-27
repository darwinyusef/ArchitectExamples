# Guía de Inicio Rápido

Esta guía te ayudará a configurar y ejecutar el proyecto en menos de 10 minutos.

## Prerequisitos

- Python 3.8+
- Java 8 o 11 (para Spark)
- Docker y Docker Compose
- 8GB RAM mínimo

## Paso 1: Clonar e Instalar

```bash
# Navegar al directorio
cd spark

# Instalar dependencias Python
pip install -r requirements.txt
```

## Paso 2: Iniciar Servicios

### Opción A: Setup Automático (Recomendado)

```bash
./scripts/setup.sh
```

### Opción B: Manual

```bash
# Crear archivo .env
cp .env.example .env

# Iniciar servicios con Docker
docker-compose up -d

# Verificar que los servicios estén corriendo
docker-compose ps
```

## Paso 3: Verificar Servicios

Espera 1-2 minutos y verifica que los servicios estén disponibles:

- **MLflow UI**: http://localhost:5000
- **Airflow UI**: http://localhost:8080 (usuario: `admin`, password: `admin`)
- **PgAdmin**: http://localhost:5050 (email: `admin@example.com`, password: `admin`)
- **PostgreSQL**: `localhost:5432`

## Paso 4: Ejecutar Notebooks

```bash
# Iniciar Jupyter
jupyter notebook

# Navegar a notebooks/ y abrir cualquier notebook
```

### Orden Recomendado

1. **01_spark_airflow_mlflow.ipynb** - Pipeline completo con orquestación
2. **02_spark_pytorch_mlflow.ipynb** - Deep Learning con PyTorch
3. **03_spark_tensorflow_mlflow.ipynb** - Modelos con TensorFlow
4. **04_spark_sklearn_mlflow.ipynb** - ML clásico y comparaciones
5. **05_spark_scipy_mathematics.ipynb** - Matemáticas avanzadas
6. **06_spark_clustering_postgres.ipynb** - Clustering y base de datos

## Paso 5: Ver Resultados en MLflow

1. Abre http://localhost:5000
2. Verás los experimentos creados por los notebooks
3. Explora métricas, parámetros y modelos guardados

## Configuración de PostgreSQL en PgAdmin

1. Abre http://localhost:5050
2. Login con `admin@example.com` / `admin`
3. Add New Server:
   - **Name**: Spark ML DB
   - **Host**: postgres (o `host.docker.internal` en Mac)
   - **Port**: 5432
   - **Database**: spark_ml_db
   - **Username**: spark_user
   - **Password**: spark_password

## Comandos Útiles

### Servicios Docker

```bash
# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f mlflow

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Eliminar todo (incluyendo datos)
docker-compose down -v
```

### MLflow

```bash
# Ver experimentos desde CLI
mlflow experiments search

# Servir un modelo
mlflow models serve -m runs:/<RUN_ID>/model -p 5001
```

### Spark

```bash
# Verificar instalación de Spark
pyspark --version

# Iniciar shell de PySpark
pyspark
```

## Troubleshooting

### Puerto ya en uso

Si algún puerto está ocupado, edita `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Cambiar puerto local
```

### Error de conexión a PostgreSQL

Espera 30 segundos más para que PostgreSQL termine de inicializar.

```bash
# Verificar estado
docker-compose logs postgres
```

### Notebooks no se conectan a servicios

Asegúrate de que las URLs en los notebooks coincidan:
- MLflow: `http://localhost:5000`
- PostgreSQL: `localhost:5432`

### Error de memoria en Spark

Reduce la memoria en los notebooks:

```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()
```

## Datos de Prueba

Todos los notebooks generan datos sintéticos automáticamente. No necesitas datasets externos para empezar.

## Próximos Pasos

1. ✅ Ejecuta todos los notebooks en orden
2. ✅ Explora los experimentos en MLflow UI
3. ✅ Revisa los datos en PostgreSQL usando PgAdmin
4. ✅ Modifica los hiperparámetros y compara resultados
5. ✅ Crea tus propios notebooks basándote en los ejemplos

## Recursos Adicionales

- [Documentación de Spark](https://spark.apache.org/docs/latest/)
- [MLflow Docs](https://mlflow.org/docs/latest/index.html)
- [Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)

## Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica la sección Troubleshooting
3. Consulta el README.md principal

¡Feliz aprendizaje! 🚀
