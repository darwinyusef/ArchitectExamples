import asyncio
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import get_settings
from services.grpc_service import serve as serve_grpc
from services.whisper_service import whisper_service
from services.rabbitmq_service import rabbitmq_service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Crear directorio temporal
Path(settings.temp_audio_dir).mkdir(exist_ok=True)

# FastAPI app
app = FastAPI(
    title="gRPC Voice Streaming API",
    description="API para streaming de audio con transcripción via Whisper y gRPC",
    version="1.0.0"
)

# CORS
# Obtener orígenes permitidos desde env o usar default
import os
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://transcript.aquicreamos.com")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Orígenes específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar"""
    logger.info("Starting up services...")
    try:
        await rabbitmq_service.connect()
        logger.info("RabbitMQ connected")
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar servicios al apagar"""
    logger.info("Shutting down services...")
    await rabbitmq_service.close()


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "gRPC Voice Streaming API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "services": {
            "whisper": "ok",
            "rabbitmq": "ok" if rabbitmq_service.connection else "disconnected",
            "grpc": "running"
        }
    }


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = None
):
    """
    Endpoint REST para transcribir audio (alternativa a gRPC)

    Args:
        file: Archivo de audio (MP3, WAV, etc.)
        language: Código de idioma (opcional)

    Returns:
        Transcripción del audio
    """
    try:
        # Validar tamaño
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)

        if size_mb > settings.max_audio_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_audio_size_mb}MB"
            )

        logger.info(
            f"Transcribe request - filename: {file.filename}, "
            f"size: {size_mb:.2f}MB, language: {language}"
        )

        # Transcribir
        result = await whisper_service.transcribe(content, language)

        # Publicar a RabbitMQ
        await rabbitmq_service.publish_transcription({
            'text': result['text'],
            'language': result['language'],
            'duration': result['duration'],
            'filename': file.filename
        })

        return JSONResponse(content={
            "success": True,
            "transcription": result['text'],
            "language": result['language'],
            "duration": result['duration'],
            "words_count": len(result['text'].split())
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_grpc_server():
    """Ejecutar servidor gRPC en background"""
    await serve_grpc()


async def main():
    """Función principal para ejecutar ambos servidores"""
    # Iniciar servidor gRPC en background
    grpc_task = asyncio.create_task(run_grpc_server())

    # Iniciar servidor FastAPI
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=settings.api_port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        grpc_task.cancel()
        try:
            await grpc_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
