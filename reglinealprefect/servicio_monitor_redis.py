import asyncio
import redis.asyncio as redis
import json
import os
from datetime import datetime
from typing import Optional

# Configuración de Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))

# Canal de Redis
CANAL_RESULTADOS = "laser:cotizaciones:resultados"

# Umbral de alerta (en COP)
UMBRAL_ALTO = 50.0


class ServicioMonitorLaser:
    def __init__(self, umbral_alerta: float = UMBRAL_ALTO):
        self.umbral_alerta = umbral_alerta
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.contador_cotizaciones = 0
        self.total_acumulado = 0.0

    async def inicializar(self):
        """Inicializa la conexión a Redis."""
        self.redis_client = redis.from_url(
            REDIS_URL,
            max_connections=REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        print(f"✅ Monitor conectado a Redis: {REDIS_URL}")

    async def procesar_resultado(self, data: dict):
        """
        Procesa un resultado de cotización y genera alertas/acciones.

        Formato esperado:
        {
            "id_solicitud": "uuid-123",
            "costo_produccion": 38.50,
            "precio_al_detal": 50.05,
            "status": "calculado"
        }
        """
        try:
            status = data.get("status")

            if status == "error":
                print(f"⚠️  ERROR en solicitud [{data.get('id_solicitud')}]: {data.get('error')}")
                return

            precio = data.get("precio_al_detal", 0)
            costo = data.get("costo_produccion", 0)
            id_solicitud = data.get("id_solicitud", "unknown")

            # Actualizar estadísticas
            self.contador_cotizaciones += 1
            self.total_acumulado += precio
            promedio = self.total_acumulado / self.contador_cotizaciones

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Análisis de Serie de Tiempo: Detectar piezas de alto valor
            if precio > self.umbral_alerta:
                print(f"🚨 ALERTA DE COSTO ALTO [{timestamp}]")
                print(f"   ID: {id_solicitud}")
                print(f"   Precio: ${precio:.2f} COP")
                print(f"   Costo: ${costo:.2f} COP")
                print(f"   ⚠️  Revisar stock de material y capacidad de producción")

                # Guardar alerta en Redis
                alerta_key = f"alertas:laser:{id_solicitud}"
                await self.redis_client.setex(
                    alerta_key,
                    3600,  # TTL de 1 hora
                    json.dumps({
                        "timestamp": timestamp,
                        "precio": precio,
                        "costo": costo,
                        "tipo": "costo_alto"
                    })
                )
            else:
                print(f"✅ Cotización estándar [{timestamp}]")
                print(f"   ID: {id_solicitud}")
                print(f"   Precio: ${precio:.2f} COP")

            # Mostrar estadísticas
            print(f"   📊 Estadísticas: {self.contador_cotizaciones} cotizaciones | Promedio: ${promedio:.2f}")
            print("-" * 60)

        except Exception as e:
            print(f"❌ Error procesando resultado: {e}")

    async def escuchar_resultados(self):
        """Escucha resultados de cotizaciones en el canal de Redis."""
        await self.pubsub.subscribe(CANAL_RESULTADOS)
        print(f"🎧 Escuchando resultados en: {CANAL_RESULTADOS}")
        print(f"📏 Umbral de alerta: ${self.umbral_alerta:.2f} COP")
        print("="*60)

        async for mensaje in self.pubsub.listen():
            if mensaje["type"] == "message":
                try:
                    data = json.loads(mensaje["data"])
                    await self.procesar_resultado(data)
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando mensaje JSON: {e}")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")

    async def run(self):
        """Inicia el servicio de monitoreo."""
        await self.inicializar()
        print("\n🔍 Monitor de Mercado Láser iniciado")
        print("="*60)

        try:
            await self.escuchar_resultados()
        except KeyboardInterrupt:
            print("\n\n⏹️  Deteniendo monitor...")
        finally:
            await self.cerrar()

    async def cerrar(self):
        """Cierra las conexiones de Redis."""
        if self.pubsub:
            await self.pubsub.unsubscribe(CANAL_RESULTADOS)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        print("✅ Conexiones cerradas")
        print(f"📊 Total de cotizaciones procesadas: {self.contador_cotizaciones}")


async def main():
    # Puedes personalizar el umbral aquí
    umbral = float(os.getenv("UMBRAL_ALERTA", str(UMBRAL_ALTO)))
    servicio = ServicioMonitorLaser(umbral_alerta=umbral)
    await servicio.run()


if __name__ == "__main__":
    asyncio.run(main())