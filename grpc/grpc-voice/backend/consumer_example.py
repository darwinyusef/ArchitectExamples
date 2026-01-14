#!/usr/bin/env python3
"""
Ejemplo de Consumer de RabbitMQ para procesar transcripciones

Este script se conecta a RabbitMQ y consume mensajes de la queue de transcripciones.
Útil para procesar las transcripciones en un servicio separado.

Uso:
    python consumer_example.py
"""

import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage
from config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def process_transcription(message_data: dict):
    """
    Procesar transcripción recibida

    Aquí puedes implementar tu lógica personalizada:
    - Guardar en base de datos
    - Enviar a otro servicio
    - Realizar análisis de sentimiento
    - Generar respuestas automáticas
    - etc.
    """
    logger.info("=" * 60)
    logger.info("Nueva transcripción recibida:")
    logger.info(f"  Session ID: {message_data.get('session_id')}")
    logger.info(f"  Texto: {message_data.get('text')}")
    logger.info(f"  Idioma: {message_data.get('language', 'N/A')}")
    logger.info(f"  Duración: {message_data.get('duration', 0):.2f}s")
    logger.info(f"  Timestamp: {message_data.get('timestamp')}")
    logger.info(f"  Es final: {message_data.get('is_final')}")

    metadata = message_data.get('metadata', {})
    logger.info(f"  Palabras: {metadata.get('words_count', 0)}")
    logger.info("=" * 60)

    # Aquí puedes agregar tu lógica personalizada
    # Por ejemplo:
    # - await save_to_database(message_data)
    # - await send_to_analytics(message_data)
    # - await generate_response(message_data)


async def on_message(message: IncomingMessage):
    """
    Callback para procesar mensajes recibidos
    """
    async with message.process():
        try:
            # Decodificar mensaje
            body = message.body.decode()
            data = json.loads(body)

            # Procesar transcripción
            await process_transcription(data)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")


async def main():
    """
    Función principal del consumer
    """
    logger.info("Starting RabbitMQ consumer...")
    logger.info(f"Connecting to: {settings.rabbitmq_url}")
    logger.info(f"Queue: {settings.rabbitmq_queue}")

    # Conectar a RabbitMQ
    connection = await connect_robust(settings.rabbitmq_url)

    async with connection:
        # Crear channel
        channel = await connection.channel()

        # Configurar QoS (procesar 1 mensaje a la vez)
        await channel.set_qos(prefetch_count=1)

        # Obtener queue
        queue = await channel.get_queue(settings.rabbitmq_queue)

        logger.info("✓ Connected to RabbitMQ")
        logger.info("Waiting for messages... (Press Ctrl+C to exit)")

        # Consumir mensajes
        await queue.consume(on_message)

        # Mantener el consumer corriendo
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("\nShutting down consumer...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
