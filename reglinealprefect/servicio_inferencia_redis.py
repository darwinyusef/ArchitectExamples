import asyncio
import numpy as np
import onnxruntime as ort
import redis.asyncio as redis
import json
import os
from typing import Optional

# Configuración de Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))

# Canales de Redis
CANAL_SOLICITUD = "laser:cotizaciones:solicitud"
CANAL_RESULTADOS = "laser:cotizaciones:resultados"

# Margen de mercado (30%)
MARGEN_MERCADO = 1.3


class ServicioInferenciaLaser:
    def __init__(self, modelo_path: str = "costos_cajas_laser.onnx"):
        self.modelo_path = modelo_path
        self.session: Optional[ort.InferenceSession] = None
        self.input_name: Optional[str] = None
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

    async def inicializar(self):
        """Inicializa el modelo ONNX y la conexión a Redis."""
        # Cargar modelo ONNX
        print(f"Cargando modelo ONNX desde: {self.modelo_path}")
        self.session = ort.InferenceSession(self.modelo_path)
        self.input_name = self.session.get_inputs()[0].name
        print(f"✅ Modelo ONNX cargado. Input name: {self.input_name}")

        # Conectar a Redis
        self.redis_client = redis.from_url(
            REDIS_URL,
            max_connections=REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        print(f"✅ Conectado a Redis: {REDIS_URL}")

    async def procesar_solicitud(self, mensaje: dict):
        """
        Procesa una solicitud de cotización.

        Formato esperado del mensaje:
        {
            "id_solicitud": "uuid-123",
            "params": [tiempo_seg, material_cm2, energia_kwh]
        }
        """
        try:
            id_solicitud = mensaje.get("id_solicitud", "unknown")
            params = mensaje.get("params")

            if not params or len(params) != 3:
                raise ValueError("Se requieren 3 parámetros: [tiempo_seg, material_cm2, energia_kwh]")

            # Preparar datos para inferencia
            input_array = np.array([params], dtype=np.float32)

            # Ejecutar inferencia ONNX
            resultado = self.session.run(None, {self.input_name: input_array})
            costo_base = float(resultado[0][0])

            # Aplicar margen de mercado
            precio_mercado = costo_base * MARGEN_MERCADO

            # Preparar respuesta
            respuesta = {
                "id_solicitud": id_solicitud,
                "costo_produccion": round(costo_base, 2),
                "precio_al_detal": round(precio_mercado, 2),
                "params": params,
                "status": "calculado",
                "margen_aplicado": MARGEN_MERCADO
            }

            # Publicar resultado en Redis
            await self.redis_client.publish(
                CANAL_RESULTADOS,
                json.dumps(respuesta)
            )

            print(f"✅ Cotización procesada [ID: {id_solicitud}] - Precio: ${precio_mercado:.2f} COP")

        except Exception as e:
            print(f"❌ Error procesando solicitud: {e}")
            # Publicar error
            error_msg = {
                "id_solicitud": mensaje.get("id_solicitud", "unknown"),
                "status": "error",
                "error": str(e)
            }
            await self.redis_client.publish(CANAL_RESULTADOS, json.dumps(error_msg))

    async def escuchar_solicitudes(self):
        """Escucha solicitudes de cotización en el canal de Redis."""
        await self.pubsub.subscribe(CANAL_SOLICITUD)
        print(f"🎧 Escuchando solicitudes en: {CANAL_SOLICITUD}")
        print("="*60)

        async for mensaje in self.pubsub.listen():
            if mensaje["type"] == "message":
                try:
                    data = json.loads(mensaje["data"])
                    await self.procesar_solicitud(data)
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando mensaje JSON: {e}")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")

    async def run(self):
        """Inicia el servicio de inferencia."""
        await self.inicializar()
        print("\n🚀 Servicio de Cotización Láser (ONNX) iniciado")
        print("="*60)

        try:
            await self.escuchar_solicitudes()
        except KeyboardInterrupt:
            print("\n\n⏹️  Deteniendo servicio...")
        finally:
            await self.cerrar()

    async def cerrar(self):
        """Cierra las conexiones de Redis."""
        if self.pubsub:
            await self.pubsub.unsubscribe(CANAL_SOLICITUD)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        print("✅ Conexiones cerradas")


async def main():
    servicio = ServicioInferenciaLaser()
    await servicio.run()


if __name__ == "__main__":
    asyncio.run(main())
