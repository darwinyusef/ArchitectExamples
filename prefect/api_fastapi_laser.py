from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import numpy as np
import onnxruntime as ort
import redis.asyncio as redis
import json
import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
import mlflow
from mlflow.tracking import MlflowClient
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración
REDIS_URL = os.getenv("REDIS_URL")
MODELO_ONNX_PATH = "costos_cajas_laser.onnx"
MARGEN_MERCADO = 1.3

# Canales de Redis
CANAL_SOLICITUD = "laser:cotizaciones:solicitud"
CANAL_RESULTADOS = "laser:cotizaciones:resultados"

# Variables globales
onnx_session: Optional[ort.InferenceSession] = None
redis_client: Optional[redis.Redis] = None
estadisticas = {
    "total_cotizaciones": 0,
    "cotizaciones_exitosas": 0,
    "errores": 0,
    "inicio_servicio": datetime.now().isoformat()
}


# Modelos Pydantic
class ParametrosCotizacion(BaseModel):
    """Parámetros para solicitar una cotización de corte láser."""
    tiempo_seg: float = Field(..., gt=0, description="Tiempo de corte en segundos")
    material_cm2: float = Field(..., gt=0, description="Área de material en cm²")
    energia_kwh: float = Field(..., gt=0, description="Energía consumida en kWh")

    @validator('tiempo_seg', 'material_cm2', 'energia_kwh')
    def validar_positivo(cls, v):
        if v <= 0:
            raise ValueError('Debe ser mayor que cero')
        return v


class RespuestaCotizacion(BaseModel):
    """Respuesta de una cotización."""
    id_cotizacion: str
    costo_produccion: float
    precio_al_detal: float
    parametros: ParametrosCotizacion
    margen_aplicado: float
    timestamp: str
    status: str = "calculado"


class ErrorRespuesta(BaseModel):
    """Respuesta de error."""
    error: str
    detalle: Optional[str] = None
    timestamp: str


class EstadisticasServicio(BaseModel):
    """Estadísticas del servicio."""
    total_cotizaciones: int
    cotizaciones_exitosas: int
    errores: int
    inicio_servicio: str
    uptime_segundos: float


class SolicitudLote(BaseModel):
    """Solicitud de múltiples cotizaciones."""
    cotizaciones: List[ParametrosCotizacion] = Field(..., max_items=50)


# Ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja la inicialización y cierre de recursos."""
    global onnx_session, redis_client

    # Inicialización
    try:
        # Cargar modelo ONNX (REQUERIDO)
        print(f"Cargando modelo ONNX: {MODELO_ONNX_PATH}")
        onnx_session = ort.InferenceSession(MODELO_ONNX_PATH)
        print(f"✅ Modelo ONNX cargado exitosamente")

    except Exception as e:
        print(f"❌ Error cargando modelo ONNX: {e}")
        print(f"💡 Ejecuta: python modelo_laser_mlflow.py")
        raise

    # Conectar a Redis (OPCIONAL)
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        print(f"✅ Conectado a Redis: {REDIS_URL}")
    except Exception as e:
        print(f"⚠️  Redis no disponible: {e}")
        print(f"⚠️  La API funcionará sin cache ni pub/sub")
        redis_client = None

    yield

    # Limpieza
    if redis_client:
        await redis_client.close()
        print("✅ Conexión a Redis cerrada")


# Crear aplicación FastAPI
app = FastAPI(
    title="API de Cotización Láser",
    description="API REST para cotización de corte láser con modelo ONNX",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorios estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Funciones auxiliares
def ejecutar_inferencia(params: ParametrosCotizacion) -> tuple[float, float]:
    """
    Ejecuta inferencia con el modelo ONNX.

    Returns:
        Tupla de (costo_produccion, precio_al_detal)
    """
    if onnx_session is None:
        raise RuntimeError("Modelo ONNX no cargado")

    # Preparar datos
    input_array = np.array(
        [[params.tiempo_seg, params.material_cm2, params.energia_kwh]],
        dtype=np.float32
    )

    # Ejecutar inferencia
    input_name = onnx_session.get_inputs()[0].name
    resultado = onnx_session.run(None, {input_name: input_array})

    # Extraer el valor (manejar diferentes estructuras de resultado)
    try:
        # Intentar obtener el primer elemento
        output = resultado[0]

        # Si es un array de NumPy, usar .item() para convertir a escalar
        if hasattr(output, 'item'):
            costo_base = float(output.item())
        elif hasattr(output, '__getitem__'):
            # Si es indexable, intentar acceder al primer elemento
            if hasattr(output[0], 'item'):
                costo_base = float(output[0].item())
            elif hasattr(output[0], '__getitem__'):
                costo_base = float(output[0][0])
            else:
                costo_base = float(output[0])
        else:
            costo_base = float(output)
    except Exception as e:
        print(f"❌ Error extrayendo resultado ONNX: {e}")
        print(f"   Estructura del resultado: {type(resultado)}, shape: {resultado[0].shape if hasattr(resultado[0], 'shape') else 'N/A'}")
        raise RuntimeError(f"Error procesando resultado del modelo ONNX: {e}")

    # Aplicar margen
    precio_mercado = costo_base * MARGEN_MERCADO

    return costo_base, precio_mercado


async def publicar_en_redis(id_cotizacion: str, respuesta: dict):
    """Publica el resultado en Redis pub/sub (si está disponible)."""
    if not redis_client:
        return  # Redis no disponible, skip silenciosamente

    try:
        await redis_client.publish(
            CANAL_RESULTADOS,
            json.dumps(respuesta)
        )
    except Exception as e:
        print(f"⚠️  Error publicando en Redis: {e}")


# Endpoints

# Página web principal con interfaz HTML
@app.get("/", response_class=HTMLResponse, tags=["Web"])
async def index(request: Request):
    """Página principal con interfaz web para cotizaciones."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api", tags=["General"])
async def api_root():
    """Endpoint raíz de la API con información."""
    return {
        "servicio": "API de Cotización Láser",
        "version": "1.0.0",
        "estado": "activo",
        "documentacion": "/docs",
        "interfaz_web": "/",
        "endpoints": {
            "cotizar": "POST /api/v1/cotizar",
            "cotizar_lote": "POST /api/v1/cotizar/lote",
            "salud": "GET /health",
            "estadisticas": "GET /stats"
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Verificar salud del servicio."""
    try:
        # Verificar modelo ONNX
        if onnx_session is None:
            raise Exception("Modelo ONNX no disponible")

        # Verificar Redis (opcional)
        redis_ok = False
        if redis_client:
            try:
                await redis_client.ping()
                redis_ok = True
            except:
                pass

        return {
            "status": "healthy",
            "modelo_onnx": "ok",
            "redis": "connected" if redis_ok else "not available (optional)",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio no disponible: {str(e)}")


@app.get("/stats", response_model=EstadisticasServicio, tags=["General"])
async def obtener_estadisticas():
    """Obtener estadísticas del servicio."""
    inicio = datetime.fromisoformat(estadisticas["inicio_servicio"])
    uptime = (datetime.now() - inicio).total_seconds()

    return EstadisticasServicio(
        total_cotizaciones=estadisticas["total_cotizaciones"],
        cotizaciones_exitosas=estadisticas["cotizaciones_exitosas"],
        errores=estadisticas["errores"],
        inicio_servicio=estadisticas["inicio_servicio"],
        uptime_segundos=uptime
    )


@app.post("/api/v1/cotizar", response_model=RespuestaCotizacion, tags=["Cotizaciones"])
async def crear_cotizacion(
    params: ParametrosCotizacion,
    background_tasks: BackgroundTasks
):
    """
    Crear una cotización de corte láser.

    Parámetros:
    - **tiempo_seg**: Tiempo de corte en segundos (> 0)
    - **material_cm2**: Área de material en cm² (> 0)
    - **energia_kwh**: Energía consumida en kWh (> 0)

    Retorna:
    - Cotización con costo de producción y precio al detal
    """
    try:
        # Generar ID único
        id_cotizacion = str(uuid.uuid4())

        # Ejecutar inferencia
        costo_produccion, precio_al_detal = ejecutar_inferencia(params)

        # Crear respuesta
        respuesta = RespuestaCotizacion(
            id_cotizacion=id_cotizacion,
            costo_produccion=round(costo_produccion, 2),
            precio_al_detal=round(precio_al_detal, 2),
            parametros=params,
            margen_aplicado=MARGEN_MERCADO,
            timestamp=datetime.now().isoformat(),
            status="calculado"
        )

        # Publicar en Redis (background) - solo si está disponible
        respuesta_dict = respuesta.dict()
        background_tasks.add_task(publicar_en_redis, id_cotizacion, respuesta_dict)

        # Guardar en Redis por 1 hora (cache) - solo si está disponible
        if redis_client:
            try:
                background_tasks.add_task(
                    redis_client.setex,
                    f"cotizacion:{id_cotizacion}",
                    3600,
                    json.dumps(respuesta_dict)
                )
            except Exception as e:
                print(f"⚠️  Error guardando en cache Redis: {e}")

        # Actualizar estadísticas
        estadisticas["total_cotizaciones"] += 1
        estadisticas["cotizaciones_exitosas"] += 1

        return respuesta

    except Exception as e:
        estadisticas["total_cotizaciones"] += 1
        estadisticas["errores"] += 1
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando cotización: {str(e)}"
        )


@app.post("/api/v1/cotizar/lote", tags=["Cotizaciones"])
async def crear_cotizaciones_lote(
    solicitud: SolicitudLote,
    background_tasks: BackgroundTasks
):
    """
    Crear múltiples cotizaciones en lote (máximo 50).

    Útil para procesar varias piezas a la vez.
    """
    resultados = []
    errores = []

    for idx, params in enumerate(solicitud.cotizaciones):
        try:
            id_cotizacion = str(uuid.uuid4())
            costo_produccion, precio_al_detal = ejecutar_inferencia(params)

            respuesta = RespuestaCotizacion(
                id_cotizacion=id_cotizacion,
                costo_produccion=round(costo_produccion, 2),
                precio_al_detal=round(precio_al_detal, 2),
                parametros=params,
                margen_aplicado=MARGEN_MERCADO,
                timestamp=datetime.now().isoformat(),
                status="calculado"
            )

            resultados.append(respuesta)

            # Publicar en Redis (background)
            respuesta_dict = respuesta.dict()
            background_tasks.add_task(publicar_en_redis, id_cotizacion, respuesta_dict)

            estadisticas["cotizaciones_exitosas"] += 1

        except Exception as e:
            errores.append({
                "indice": idx,
                "parametros": params.dict(),
                "error": str(e)
            })
            estadisticas["errores"] += 1

    estadisticas["total_cotizaciones"] += len(solicitud.cotizaciones)

    return {
        "total_procesadas": len(solicitud.cotizaciones),
        "exitosas": len(resultados),
        "errores": len(errores),
        "resultados": resultados,
        "detalles_errores": errores if errores else None
    }


@app.get("/api/v1/cotizar/{id_cotizacion}", tags=["Cotizaciones"])
async def obtener_cotizacion(id_cotizacion: str):
    """
    Obtener una cotización por su ID (si existe en cache de Redis).

    Las cotizaciones se almacenan por 1 hora en Redis.
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible"
        )

    try:
        resultado = await redis_client.get(f"cotizacion:{id_cotizacion}")

        if not resultado:
            raise HTTPException(
                status_code=404,
                detail=f"Cotización {id_cotizacion} no encontrada o expirada"
            )

        return json.loads(resultado)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo cotización: {str(e)}"
        )


@app.get("/api/v1/productos", tags=["Productos"])
async def obtener_productos_predefinidos():
    """
    Obtener especificaciones de productos predefinidos.

    Estos son los productos usados para entrenar el modelo.
    """
    productos = {
        'Caja 1 (Pequeña)': {
            "tiempo_seg": 360,
            "material_cm2": 24,
            "energia_kwh": 0.025,
            "descripcion": "Caja pequeña de corte láser"
        },
        'Caja 2 (Mediana)': {
            "tiempo_seg": 240,
            "material_cm2": 26,
            "energia_kwh": 0.016,
            "descripcion": "Caja mediana de corte láser"
        },
        'Caja 3 (Grande)': {
            "tiempo_seg": 300,
            "material_cm2": 48,
            "energia_kwh": 0.020,
            "descripcion": "Caja grande de corte láser"
        }
    }
    return productos


@app.post("/api/v1/productos/{nombre}/cotizar", tags=["Productos"])
async def cotizar_producto_predefinido(
    nombre: str,
    background_tasks: BackgroundTasks
):
    """
    Cotizar un producto predefinido por su nombre.

    Productos disponibles:
    - Caja 1 (Pequeña)
    - Caja 2 (Mediana)
    - Caja 3 (Grande)
    """
    productos = {
        'caja-1': ParametrosCotizacion(tiempo_seg=360, material_cm2=24, energia_kwh=0.025),
        'caja-2': ParametrosCotizacion(tiempo_seg=240, material_cm2=26, energia_kwh=0.016),
        'caja-3': ParametrosCotizacion(tiempo_seg=300, material_cm2=48, energia_kwh=0.020)
    }

    nombre_normalizado = nombre.lower().replace(' ', '-')

    if nombre_normalizado not in productos:
        raise HTTPException(
            status_code=404,
            detail=f"Producto '{nombre}' no encontrado. Productos disponibles: {list(productos.keys())}"
        )

    return await crear_cotizacion(productos[nombre_normalizado], background_tasks)




# Ejecutar con: uvicorn api_fastapi_laser:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_fastapi_laser:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
