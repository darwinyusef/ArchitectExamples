#!/usr/bin/env python3
"""
Script para probar conexión a RabbitMQ y operaciones básicas.
Usa credenciales de .env o argumentos de línea de comandos.
"""

import sys
import os
import pika
import json
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

# Cargar variables de entorno
load_dotenv()


def test_rabbitmq_connection(
    host: str = None,
    port: int = 5672,
    username: str = None,
    password: str = None
):
    """Probar conexión y operaciones básicas en RabbitMQ."""

    # Si no se proporcionan credenciales, usar de .env
    if not host or not username or not password:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "")
        if rabbitmq_url:
            # Parsear URL: amqp://user:pass@host:port/
            parsed = urlparse(rabbitmq_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5672
            username = parsed.username or "guest"
            password = parsed.password or "guest"
        else:
            print("❌ Error: No se encontró RABBITMQ_URL en .env")
            print("   Proporciona credenciales como argumentos:")
            print("   python test_rabbitmq.py <username> <password> [host] [port]")
            return False

    print(f"🐰 Conectando a RabbitMQ: {host}:{port}")
    print("-" * 60)

    try:
        # Test 1: Conexión
        print("\n✅ Test 1: Conexión")
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            heartbeat=60
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        print(f"   Conectado a RabbitMQ en {host}:{port}")

        # Test 2: Declarar Exchange
        print("\n✅ Test 2: Declarar Exchange")
        exchange_name = "ai_goals_tracker"
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True
        )
        print(f"   Exchange '{exchange_name}' declarado (topic, durable)")

        # Test 3: Declarar Queue
        print("\n✅ Test 3: Declarar Queue de Prueba")
        queue_name = "ai_goals_tracker_test"
        result = channel.queue_declare(
            queue=queue_name,
            durable=True
        )
        print(f"   Queue '{queue_name}' creada")
        print(f"   Mensajes en cola: {result.method.message_count}")

        # Test 4: Bind Queue a Exchange
        print("\n✅ Test 4: Bind Queue a Exchange")
        routing_key = "test.message"
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        print(f"   Queue '{queue_name}' vinculada a '{exchange_name}'")
        print(f"   Routing key: '{routing_key}'")

        # Test 5: Publicar Mensaje
        print("\n✅ Test 5: Publicar Mensaje")
        message = {
            "event_type": "test.connection",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "message": "¡Conexión exitosa desde AI Goals Tracker V2!",
                "test_id": "test_001"
            }
        }

        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistente
                content_type='application/json'
            )
        )
        print(f"   Mensaje publicado: {message['event_type']}")

        # Test 6: Consumir Mensaje
        print("\n✅ Test 6: Consumir Mensaje")

        def callback(ch, method, properties, body):
            """Callback para procesar mensajes."""
            msg = json.loads(body.decode('utf-8'))
            print(f"   Mensaje recibido: {msg['event_type']}")
            print(f"   Payload: {msg['payload']['message']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )

        # Consumir solo un mensaje
        method, properties, body = channel.basic_get(queue_name, auto_ack=False)
        if method:
            msg = json.loads(body.decode('utf-8'))
            print(f"   Mensaje consumido: {msg['event_type']}")
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("   No hay mensajes en la cola")

        # Test 7: Estadísticas de la Queue
        print("\n✅ Test 7: Estadísticas de Queue")
        result = channel.queue_declare(queue=queue_name, passive=True)
        print(f"   Nombre: {queue_name}")
        print(f"   Mensajes: {result.method.message_count}")
        print(f"   Consumidores: {result.method.consumer_count}")

        # Test 8: Limpiar (opcional)
        print("\n🧹 Limpieza")
        # Eliminar queue de prueba
        channel.queue_delete(queue=queue_name)
        print(f"   Queue '{queue_name}' eliminada")

        # Cerrar conexión
        connection.close()

        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        print(f"\nRabbitMQ está funcionando correctamente en: {host}:{port}")
        print(f"Credenciales: {username} / {'*' * len(password)}")

        return True

    except pika.exceptions.AMQPConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\nVerificar:")
        print(f"  1. El servidor RabbitMQ está corriendo en {host}:{port}")
        print(f"  2. Las credenciales son correctas: {username}")
        print("  3. No hay firewall bloqueando el puerto 5672")
        return False

    except pika.exceptions.AMQPChannelError as e:
        print(f"\n❌ Error de canal: {e}")
        print("\nEl usuario puede no tener permisos suficientes.")
        return False

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Usar credenciales de argumentos si se proporcionan
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        host = sys.argv[3] if len(sys.argv) >= 4 else None
        port = int(sys.argv[4]) if len(sys.argv) >= 5 else 5672
        success = test_rabbitmq_connection(
            host=host,
            port=port,
            username=username,
            password=password
        )
    else:
        # Usar credenciales de .env
        success = test_rabbitmq_connection()

    sys.exit(0 if success else 1)
