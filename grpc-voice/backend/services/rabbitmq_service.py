import json
import logging
from typing import Dict, Any
import aio_pika
from aio_pika import ExchangeType
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        """Conectar a RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()

            # Declarar exchange
            self.exchange = await self.channel.declare_exchange(
                settings.rabbitmq_exchange,
                ExchangeType.TOPIC,
                durable=True
            )

            # Declarar queue
            queue = await self.channel.declare_queue(
                settings.rabbitmq_queue,
                durable=True
            )

            # Bind queue to exchange
            await queue.bind(
                self.exchange,
                routing_key=settings.rabbitmq_routing_key
            )

            logger.info(f"Connected to RabbitMQ: {settings.rabbitmq_url}")

        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise

    async def publish_transcription(self, transcription_data: Dict[str, Any]):
        """Publicar transcripción a RabbitMQ"""
        try:
            if not self.exchange:
                await self.connect()

            message_body = json.dumps(transcription_data, ensure_ascii=False)

            message = aio_pika.Message(
                body=message_body.encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.exchange.publish(
                message,
                routing_key=settings.rabbitmq_routing_key
            )

            logger.info(f"Published transcription: session_id={transcription_data.get('session_id')}")

        except Exception as e:
            logger.error(f"Error publishing to RabbitMQ: {e}")
            raise

    async def close(self):
        """Cerrar conexión"""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")


# Singleton instance
rabbitmq_service = RabbitMQService()
