"""
Test de conexión a Redis usando redis.asyncio (mismo que FastAPI)
"""

import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

async def test_redis_connection():
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    print(f"🔍 Intentando conectar a: {REDIS_URL}")

    try:
        # Crear cliente (igual que en FastAPI)
        client = redis.from_url(REDIS_URL, decode_responses=True)

        # Probar ping
        await client.ping()
        print("✅ Conexión exitosa con redis.asyncio")

        # Probar set/get
        await client.set("test_key", "test_value")
        value = await client.get("test_key")
        print(f"✅ Set/Get funciona: {value}")

        # Limpiar
        await client.delete("test_key")

        # Cerrar
        await client.close()

        print("\n🎉 Redis funciona correctamente con redis.asyncio")
        print("La aplicación FastAPI debería conectarse sin problemas.")

        return True

    except redis.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print(f"   1. URL en .env: {REDIS_URL}")
        print("   2. Redis esté corriendo en 64.23.150.221:6379")
        print("   3. Firewall no bloquee la conexión")
        return False

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TEST: Redis Async (mismo que FastAPI)")
    print("="*60)
    print()

    resultado = asyncio.run(test_redis_connection())

    if resultado:
        print("\n✅ Todo OK. Inicia la API:")
        print("   python api_fastapi_laser.py")
    else:
        print("\n❌ Hay un problema con Redis.")
