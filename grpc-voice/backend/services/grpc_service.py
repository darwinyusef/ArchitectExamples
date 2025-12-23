import logging
import time
import uuid
from typing import Iterator
import grpc
from concurrent import futures

# Imports que se generarán desde el proto
import sys
sys.path.append('..')
from proto import audio_service_pb2, audio_service_pb2_grpc

from services.whisper_service import whisper_service
from services.rabbitmq_service import rabbitmq_service
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AudioStreamServicer(audio_service_pb2_grpc.AudioStreamServiceServicer):
    """Implementación del servicio gRPC de audio streaming"""

    async def StreamAudio(
        self,
        request_iterator: Iterator[audio_service_pb2.AudioChunk],
        context: grpc.aio.ServicerContext
    ) -> Iterator[audio_service_pb2.TranscriptionResponse]:
        """
        Streaming bidireccional: recibe chunks de audio y envía transcripciones

        Args:
            request_iterator: Iterator de AudioChunk
            context: Contexto gRPC

        Yields:
            TranscriptionResponse
        """
        session_data = {}
        session_id = None

        try:
            async for chunk in request_iterator:
                session_id = chunk.session_id or str(uuid.uuid4())

                # Acumular chunks por sesión
                if session_id not in session_data:
                    session_data[session_id] = {
                        'chunks': [],
                        'metadata': chunk.metadata
                    }

                session_data[session_id]['chunks'].append(chunk.audio_data)
                logger.info(
                    f"Received chunk {chunk.chunk_index} for session {session_id}, "
                    f"size: {len(chunk.audio_data)} bytes"
                )

                # Cuando se recibe suficiente audio, procesar
                total_size = sum(len(c) for c in session_data[session_id]['chunks'])

                # Procesar cada ~500KB o cuando se termine el stream
                if total_size >= 500000:  # 500KB
                    audio_data = b''.join(session_data[session_id]['chunks'])
                    session_data[session_id]['chunks'] = []  # Limpiar chunks procesados

                    # Transcribir
                    transcription_result = await self._process_audio(
                        audio_data,
                        session_id,
                        chunk.metadata,
                        is_final=False
                    )

                    yield transcription_result

            # Procesar chunks restantes
            if session_id and session_data[session_id]['chunks']:
                audio_data = b''.join(session_data[session_id]['chunks'])
                metadata = session_data[session_id]['metadata']

                transcription_result = await self._process_audio(
                    audio_data,
                    session_id,
                    metadata,
                    is_final=True
                )

                yield transcription_result

        except Exception as e:
            logger.error(f"Error in StreamAudio: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def TranscribeAudio(
        self,
        request: audio_service_pb2.AudioFile,
        context: grpc.aio.ServicerContext
    ) -> audio_service_pb2.TranscriptionResponse:
        """
        Método unario: transcribir un archivo de audio completo

        Args:
            request: AudioFile
            context: Contexto gRPC

        Returns:
            TranscriptionResponse
        """
        try:
            session_id = str(uuid.uuid4())
            logger.info(
                f"TranscribeAudio request - session: {session_id}, "
                f"filename: {request.filename}, size: {len(request.audio_data)} bytes"
            )

            result = await self._process_audio(
                request.audio_data,
                session_id,
                request.metadata,
                is_final=True
            )

            return result

        except Exception as e:
            logger.error(f"Error in TranscribeAudio: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def _process_audio(
        self,
        audio_data: bytes,
        session_id: str,
        metadata: audio_service_pb2.AudioMetadata,
        is_final: bool
    ) -> audio_service_pb2.TranscriptionResponse:
        """
        Procesar audio: transcribir y publicar a RabbitMQ

        Args:
            audio_data: Bytes del audio
            session_id: ID de sesión
            metadata: Metadata del audio
            is_final: Si es la transcripción final

        Returns:
            TranscriptionResponse
        """
        try:
            # Transcribir con Whisper
            language = metadata.language if metadata.language else None
            transcription = await whisper_service.transcribe(audio_data, language)

            # Crear respuesta
            response = audio_service_pb2.TranscriptionResponse(
                text=transcription['text'],
                session_id=session_id,
                confidence=1.0,  # Whisper no provee confianza directamente
                timestamp=int(time.time()),
                is_final=is_final,
                metadata=audio_service_pb2.TranscriptionMetadata(
                    duration=transcription.get('duration', 0),
                    language_detected=transcription.get('language', 'unknown'),
                    words_count=len(transcription['text'].split())
                )
            )

            # Publicar a RabbitMQ
            await self._publish_to_rabbitmq(response, transcription)

            logger.info(
                f"Transcription completed - session: {session_id}, "
                f"text_length: {len(response.text)}, is_final: {is_final}"
            )

            return response

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise

    async def _publish_to_rabbitmq(
        self,
        response: audio_service_pb2.TranscriptionResponse,
        transcription: dict
    ):
        """Publicar transcripción a RabbitMQ"""
        try:
            message_data = {
                'session_id': response.session_id,
                'text': response.text,
                'confidence': response.confidence,
                'timestamp': response.timestamp,
                'is_final': response.is_final,
                'metadata': {
                    'duration': response.metadata.duration,
                    'language_detected': response.metadata.language_detected,
                    'words_count': response.metadata.words_count
                },
                'segments': transcription.get('segments', [])
            }

            await rabbitmq_service.publish_transcription(message_data)

        except Exception as e:
            logger.error(f"Error publishing to RabbitMQ: {e}")
            # No fallar la transcripción si RabbitMQ falla


async def serve():
    """Iniciar servidor gRPC"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
        ]
    )

    audio_service_pb2_grpc.add_AudioStreamServiceServicer_to_server(
        AudioStreamServicer(), server
    )

    # Habilitar reflection para debugging
    from grpc_reflection.v1alpha import reflection
    SERVICE_NAMES = (
        audio_service_pb2.DESCRIPTOR.services_by_name['AudioStreamService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Conectar a RabbitMQ
    await rabbitmq_service.connect()

    # Iniciar servidor
    listen_addr = f'[::]:{settings.grpc_port}'
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting gRPC server on {listen_addr}")

    await server.start()
    logger.info("gRPC server started successfully")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        await rabbitmq_service.close()
        await server.stop(grace=5)
