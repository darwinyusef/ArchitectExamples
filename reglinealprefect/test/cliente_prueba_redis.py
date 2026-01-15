import asyncio
import redis.asyncio as redis
import json
import os
import uuid
from typing import List

# Configuración de Redis
REDIS_URL = os.getenv("REDIS_URL")
CANAL_SOLICITUD = "laser:cotizaciones:solicitud"


async def enviar_solicitud_cotizacion(
    tiempo_seg: float,
    material_cm2: float,
    energia_kwh: float
) -> str:
    """
    Envía una solicitud de cotización al servicio de inferencia.

    Args:
        tiempo_seg: Tiempo de corte en segundos
        material_cm2: Área de material en cm²
        energia_kwh: Energía consumida en kWh

    Returns:
        ID de la solicitud
    """
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    try:
        # Generar ID único para la solicitud
        id_solicitud = str(uuid.uuid4())

        # Preparar mensaje
        solicitud = {
            "id_solicitud": id_solicitud,
            "params": [tiempo_seg, material_cm2, energia_kwh]
        }

        # Publicar solicitud
        await redis_client.publish(CANAL_SOLICITUD, json.dumps(solicitud))

        print(f"✅ Solicitud enviada [ID: {id_solicitud}]")
        print(f"   Parámetros: tiempo={tiempo_seg}s, material={material_cm2}cm², energía={energia_kwh}kWh")

        return id_solicitud

    finally:
        await redis_client.close()


async def enviar_solicitudes_muestra():
    """Envía varias solicitudes de muestra basadas en las especificaciones de productos."""

    print("\n🚀 Cliente de Prueba - Cotizaciones Láser")
    print("="*60)

    # Especificaciones de productos de ejemplo (del modelo original)
    productos = {
        'Caja 1 (Pequeña)': [360, 24, 0.025],
        'Caja 2 (Mediana)': [240, 26, 0.016],
        'Caja 3 (Grande)': [300, 48, 0.020],
        'Pieza Personalizada 1': [450, 35, 0.030],  # Pieza que debería generar alerta
        'Pieza Personalizada 2': [500, 60, 0.040],  # Pieza grande que debería generar alerta
    }

    for nombre, params in productos.items():
        print(f"\n📦 Solicitando cotización para: {nombre}")
        await enviar_solicitud_cotizacion(
            tiempo_seg=params[0],
            material_cm2=params[1],
            energia_kwh=params[2]
        )

        # Pequeña pausa entre solicitudes
        await asyncio.sleep(1)

    print("\n" + "="*60)
    print("✅ Todas las solicitudes enviadas")
    print("💡 Revisa los servicios de inferencia y monitor para ver los resultados")


async def enviar_solicitud_personalizada():
    """Envía una solicitud personalizada desde input del usuario."""

    print("\n🎯 Solicitud de Cotización Personalizada")
    print("="*60)

    try:
        tiempo = float(input("Tiempo de corte (segundos): "))
        material = float(input("Área de material (cm²): "))
        energia = float(input("Energía consumida (kWh): "))

        await enviar_solicitud_cotizacion(tiempo, material, energia)

    except ValueError:
        print("❌ Error: Valores inválidos. Usa números.")
    except KeyboardInterrupt:
        print("\n❌ Cancelado por usuario")


async def main():
    """Función principal del cliente."""

    print("\n" + "="*60)
    print("CLIENTE DE PRUEBA - SISTEMA DE COTIZACIÓN LÁSER")
    print("="*60)
    print("\nOpciones:")
    print("1. Enviar solicitudes de muestra (5 productos)")
    print("2. Enviar solicitud personalizada")
    print("3. Enviar solicitud rápida (Caja Grande)")

    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()

        if opcion == "1":
            await enviar_solicitudes_muestra()
        elif opcion == "2":
            await enviar_solicitud_personalizada()
        elif opcion == "3":
            print("\n📦 Enviando solicitud rápida: Caja Grande")
            await enviar_solicitud_cotizacion(300, 48, 0.020)
        else:
            print("❌ Opción inválida")

    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por usuario")


if __name__ == "__main__":
    asyncio.run(main())