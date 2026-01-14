# Sistema de Cotización Láser - FastAPI + ONNX

Sistema de cotización de corte láser con modelo de Machine Learning (ONNX) y API REST con interfaz web.

## Requisitos

- Python 3.9 o superior
- pip
- **Redis es OPCIONAL** (la aplicación funciona sin él)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd G:\ArchitectExamples\prefect
```

### 2. Instalar dependencias

```bash
pip install -r requirements_redis.txt
```

### 3. Generar el modelo ONNX con Prefect + MLflow

```bash
python modelo_laser_mlflow.py
```

Este comando:
- Ejecuta el pipeline de Prefect para entrenar el modelo
- Registra métricas y artefactos en MLflow
- Genera el archivo `costos_cajas_laser.onnx` necesario para las inferencias

## Ejecución

### Iniciar el servidor de cotizaciones

```bash
python api_fastapi_laser.py
```

El servidor iniciará en: http://localhost:8000

**Nota:** Verás un mensaje sobre Redis no disponible. Esto es normal y la API funciona perfectamente sin Redis.

### Ver el pipeline de Prefect (Opcional)

Para visualizar las ejecuciones del pipeline de entrenamiento:

```bash
prefect server start
```

Luego abre: http://localhost:4200

Ejecuta nuevamente el entrenamiento para ver el flow en la UI:
```bash
python modelo_laser_mlflow.py
```

### Ver experimentos de MLflow (Opcional)

Para visualizar métricas, modelos y artefactos de MLflow:

```bash
mlflow ui
```

Luego abre: http://localhost:5000

## Uso

### Interfaces Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Interfaz Web de Cotización** | http://localhost:8000 | Cotizar productos en tiempo real |
| **🆕 MLOps Dashboard** | http://localhost:8000/mlops | **Gestión de experimentos y modelos MLflow** |
| **API Docs (Swagger)** | http://localhost:8000/docs | Documentación interactiva de la API |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Documentación alternativa |
| **Prefect UI** | http://localhost:4200 | Visualizar pipelines de entrenamiento |
| **MLflow UI** | http://localhost:5000 | Explorar experimentos y métricas (nativo) |

### Ejemplo de uso con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/cotizar" \
  -H "Content-Type: application/json" \
  -d '{
    "tiempo_seg": 360,
    "material_cm2": 24,
    "energia_kwh": 0.025
  }'
```

### Ejemplo de uso con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/cotizar",
    json={
        "tiempo_seg": 360,
        "material_cm2": 24,
        "energia_kwh": 0.025
    }
)

print(response.json())
```

## Verificar Instalación

```bash
python verificar_instalacion.py
```

## Estructura del Proyecto

```
prefect/
├── modelo_laser_mlflow.py          # Pipeline Prefect + MLflow (entrenamiento)
├── costos_cajas_laser.onnx         # Modelo ONNX (generado)
│
├── api_fastapi_laser.py            # Servidor API REST + Web
├── templates/
│   └── index.html                  # Interfaz web
├── static/
│   ├── css/styles.css              # Estilos
│   └── js/main.js                  # JavaScript
│
├── servicio_inferencia_redis.py   # Servicio pub/sub (opcional)
├── servicio_monitor_redis.py      # Monitor de alertas (opcional)
├── cliente_prueba_redis.py        # Cliente de prueba (opcional)
│
├── mlruns/                         # Directorio de MLflow (auto-generado)
├── requirements_redis.txt          # Dependencias
└── README.md                       # Este archivo
```

## Workflow Completo

### 1. Entrenar y Visualizar con Prefect + MLflow

```bash
# Terminal 1: Iniciar Prefect UI
prefect server start

# Terminal 2: Iniciar MLflow UI
mlflow ui

# Terminal 3: Ejecutar entrenamiento
python modelo_laser_mlflow.py
```

Ahora puedes:
- Ver el flow en **Prefect UI**: http://localhost:4200
- Ver métricas en **MLflow UI**: http://localhost:5000

### 2. Usar el Modelo en Producción

```bash
# Iniciar API de cotizaciones
python api_fastapi_laser.py
```

Accede a la interfaz web: http://localhost:8000

## Troubleshooting

### Error: "Modelo ONNX no encontrado"

**Solución:** Ejecuta el pipeline de entrenamiento:
```bash
python modelo_laser_mlflow.py
```

### Error: "ModuleNotFoundError: No module named 'prefect'"

**Solución:** Instala las dependencias:
```bash
pip install -r requirements_redis.txt
```

### Error: "Puerto 8000 en uso"

**Solución:** Cambia el puerto:
```bash
uvicorn api_fastapi_laser:app --port 8080
```
Luego accede a http://localhost:8080

### Error: "Puerto 4200 en uso" (Prefect)

**Solución:** Cambia el puerto de Prefect:
```bash
prefect config set PREFECT_SERVER_API_PORT=4201
prefect server start
```

### Error: "Puerto 5000 en uso" (MLflow)

**Solución:** Cambia el puerto de MLflow:
```bash
mlflow ui --port 5001
```

### Error: "No se puede conectar a Redis"

**Solución:** ¡La API ahora funciona perfectamente sin Redis!

Verás este mensaje al iniciar:
```
⚠️  Redis no disponible: ...
⚠️  La API funcionará sin cache ni pub/sub
```

Esto es normal y esperado. La aplicación funciona completamente.

**Si quieres habilitar Redis (opcional):**
```bash
# Windows: Descargar desde https://github.com/microsoftarchive/redis/releases
redis-server

# Docker:
docker run -d -p 6379:6379 redis:alpine

# Luego reinicia la API
python api_fastapi_laser.py
```

Ver `SOLUCION_REDIS.md` para más detalles.

## Endpoints Principales

### Interfaz Web
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz de cotizaciones |
| **`/mlops`** | GET | **Dashboard MLOps** 🆕 |
| `/docs` | GET | Documentación API (Swagger) |

### API REST - Cotizaciones
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado del servicio |
| `/stats` | GET | Estadísticas |
| `/api/v1/cotizar` | POST | Crear cotización |
| `/api/v1/cotizar/lote` | POST | Cotizaciones en lote |
| `/api/v1/productos` | GET | Lista de productos |

### API REST - MLOps 🆕
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/mlops/summary` | GET | Resumen de MLflow |
| `/api/mlops/experiments` | GET | Listar experimentos |
| `/api/mlops/experiments/{id}/runs` | GET | Runs de experimento |
| `/api/mlops/runs/{id}` | GET | Detalles de run |
| `/api/mlops/runs/compare` | GET | Comparar runs |
| `/api/mlops/models` | GET | Modelos registrados |

## Parámetros de Cotización

```json
{
  "tiempo_seg": 360,      // Tiempo de corte en segundos (> 0)
  "material_cm2": 24,     // Área de material en cm² (> 0)
  "energia_kwh": 0.025    // Energía consumida en kWh (> 0)
}
```

## Respuesta de Cotización

```json
{
  "id_cotizacion": "550e8400-e29b-41d4-a716-446655440000",
  "costo_produccion": 38.50,
  "precio_al_detal": 50.05,
  "parametros": {
    "tiempo_seg": 360,
    "material_cm2": 24,
    "energia_kwh": 0.025
  },
  "margen_aplicado": 1.3,
  "timestamp": "2024-01-15T10:30:00",
  "status": "calculado"
}
```

## Productos Predefinidos

- **Caja 1 (Pequeña)**: 360s, 24cm², 0.025kWh
- **Caja 2 (Mediana)**: 240s, 26cm², 0.016kWh
- **Caja 3 (Grande)**: 300s, 48cm², 0.020kWh

## Tests

### Tests completos de la API
```bash
python test_api_laser.py
```

### Test rápido sin Redis
```bash
python test_sin_redis.py
```

Este test verifica que todo funcione correctamente sin Redis.

## Explorando MLOps

### Opción 1: MLOps Dashboard Integrado (Recomendado) 🆕

Abre: **http://localhost:8000/mlops**

Desde la interfaz web integrada puedes:

1. **Ver Resumen de MLflow**
   - Total de experimentos
   - Runs ejecutados
   - Modelos registrados
   - Modelos en producción

2. **Explorar Experimentos**
   - Lista de todos los experimentos
   - Click en un experimento para ver sus runs

3. **Analizar Runs**
   - Ver métricas principales (R², MSE, RMSE, MAE)
   - Comparar múltiples runs (selecciona checkboxes)
   - Ver detalles completos: parámetros, métricas, artefactos
   - Descargar artefactos directamente

4. **Gestionar Modelos**
   - Ver modelos registrados
   - Ver versiones y stages
   - Links al MLflow UI nativo

**Ventajas del Dashboard Integrado:**
- No necesitas cambiar de aplicación
- Interfaz simplificada y enfocada
- Comparación visual de runs
- Navegación entre Cotizaciones ↔ MLOps

### Opción 2: MLflow UI Nativo

Abre: **http://localhost:5000**

Interfaz completa de MLflow con todas las funcionalidades avanzadas.

### Ver flows de Prefect

Abre: **http://localhost:4200**

1. Ve a "Flow Runs"
2. Verás `Pipeline de Modelo de Costos Láser`
3. Explora:
   - Estado de cada tarea
   - Logs detallados
   - Tiempo de ejecución
   - Gráfico de dependencias

## Detener los Servicios

Presiona `Ctrl+C` en cada terminal:
- Terminal con FastAPI (puerto 8000)
- Terminal con MLflow (puerto 5000)
- Terminal con Prefect (puerto 4200)

## Documentación Adicional

- `README_FASTAPI.md` - Documentación completa de la API
- `README_WEB_INTERFACE.md` - Documentación de la interfaz web
- `README_REDIS_PUBSUB.md` - Sistema pub/sub con Redis (opcional)
- `INICIO_RAPIDO.md` - Guía rápida de inicio

## Licencia

Este proyecto es un ejemplo educativo para demostrar integración de FastAPI con ONNX Runtime.
