#!/usr/bin/env python3
"""
Script para probar conexión a Redis y operaciones básicas.
Usa REDIS_URL de .env o argumento de línea de comandos.
"""

import sys
import os
import redis
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def test_redis_connection(redis_url: str = None):
    """Probar conexión y operaciones básicas en Redis."""

    # Si no se proporciona URL, usar de .env
    if not redis_url:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        print(f"ℹ️  Usando REDIS_URL de .env")
    else:
        print(f"ℹ️  Usando URL proporcionada por argumento")

    print(f"🔌 Conectando a Redis: {redis_url}")
    print("-" * 60)

    try:
        # Conectar
        r = redis.from_url(redis_url, decode_responses=True)

        # Test 1: PING
        print("\n✅ Test 1: PING")
        result = r.ping()
        print(f"   Resultado: {result}")
        assert result is True, "PING failed"

        # Test 2: INFO
        print("\n✅ Test 2: INFO Server")
        info = r.info("server")
        print(f"   Redis Version: {info.get('redis_version')}")
        print(f"   OS: {info.get('os')}")
        print(f"   Uptime: {info.get('uptime_in_days')} días")

        # Test 3: SET/GET
        print("\n✅ Test 3: SET/GET")
        test_key = "ai_goals_tracker:test"
        test_value = f"Hello from AI Goals Tracker! {datetime.now()}"
        r.set(test_key, test_value)
        retrieved = r.get(test_key)
        print(f"   Set: {test_value}")
        print(f"   Get: {retrieved}")
        assert retrieved == test_value, "SET/GET mismatch"

        # Test 4: SETEX (con expiración)
        print("\n✅ Test 4: SETEX (con TTL)")
        temp_key = "ai_goals_tracker:temp"
        r.setex(temp_key, 60, "This expires in 60 seconds")
        ttl = r.ttl(temp_key)
        print(f"   TTL: {ttl} segundos")
        assert ttl > 0, "TTL not set"

        # Test 5: Hash operations (simular user session)
        print("\n✅ Test 5: HASH Operations (User Session)")
        session_key = "user_session:test-user-123"
        session_data = {
            "connection_id": "ws_conn_abc123",
            "current_goal_id": "goal-xyz",
            "mood_score": "0.85",
            "last_activity": datetime.now().isoformat()
        }
        r.hset(session_key, mapping=session_data)
        retrieved_session = r.hgetall(session_key)
        print(f"   Session guardada: {len(session_data)} campos")
        print(f"   Session recuperada: {len(retrieved_session)} campos")
        assert len(retrieved_session) == len(session_data), "Hash mismatch"

        # Test 6: KEYS (listar)
        print("\n✅ Test 6: KEYS (listar keys)")
        all_keys = r.keys("ai_goals_tracker:*")
        print(f"   Keys encontradas: {len(all_keys)}")
        for key in all_keys[:5]:  # Mostrar solo las primeras 5
            print(f"   - {key}")

        # Test 7: Memory info
        print("\n✅ Test 7: Memory Info")
        memory = r.info("memory")
        used_memory = memory.get("used_memory_human")
        peak_memory = memory.get("used_memory_peak_human")
        print(f"   Memoria usada: {used_memory}")
        print(f"   Pico de memoria: {peak_memory}")

        # Test 8: Stats
        print("\n✅ Test 8: Stats")
        stats = r.info("stats")
        total_commands = stats.get("total_commands_processed")
        total_connections = stats.get("total_connections_received")
        print(f"   Total comandos procesados: {total_commands:,}")
        print(f"   Total conexiones: {total_connections:,}")

        # Cleanup
        print("\n🧹 Limpieza de keys de prueba...")
        r.delete(test_key, temp_key, session_key)
        print("   Keys de prueba eliminadas")

        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        print(f"\nRedis está funcionando correctamente en: {redis_url}")

        return True

    except redis.ConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\nVerificar:")
        print("  1. El servidor Redis está corriendo")
        print("  2. La IP/puerto son correctos")
        print("  3. No hay firewall bloqueando el puerto 6379")
        return False

    except redis.AuthenticationError as e:
        print(f"\n❌ Error de autenticación: {e}")
        print("\nEl servidor Redis requiere password.")
        print("Actualizar REDIS_URL a: redis://:password@64.23.150.221:6379/0")
        return False

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Usar URL de argumentos si se proporciona
    redis_url = sys.argv[1] if len(sys.argv) > 1 else "redis://64.23.150.221:6379/0"

    success = test_redis_connection(redis_url)
    sys.exit(0 if success else 1)
