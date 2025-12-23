import os
import logging
import tempfile
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WhisperService:
    def __init__(self):
        self.model = None
        self.use_api = settings.whisper_api_url is not None

        if not self.use_api:
            # Cargar modelo local de Whisper
            import whisper
            logger.info(f"Loading Whisper model: {settings.whisper_model}")
            self.model = whisper.load_model(
                settings.whisper_model,
                device=settings.whisper_device
            )
            logger.info("Whisper model loaded successfully")

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribir audio usando Whisper

        Args:
            audio_data: Bytes del archivo de audio
            language: Código de idioma (opcional)

        Returns:
            Dict con la transcripción y metadata
        """
        try:
            # Guardar audio temporalmente
            temp_dir = Path(settings.temp_audio_dir)
            temp_dir.mkdir(exist_ok=True)

            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                dir=temp_dir,
                delete=False
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                if self.use_api:
                    result = await self._transcribe_api(temp_path, language)
                else:
                    result = await self._transcribe_local(temp_path, language)

                return result
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    async def _transcribe_local(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribir usando modelo local"""
        try:
            options = {}
            if language:
                options['language'] = language

            result = self.model.transcribe(audio_path, **options)

            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'duration': result.get('duration', 0),
                'segments': result.get('segments', [])
            }

        except Exception as e:
            logger.error(f"Error in local transcription: {e}")
            raise

    async def _transcribe_api(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribir usando API externa de Whisper"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                with open(audio_path, 'rb') as audio_file:
                    files = {'file': audio_file}
                    data = {}
                    if language:
                        data['language'] = language

                    response = await client.post(
                        f"{settings.whisper_api_url}/transcribe",
                        files=files,
                        data=data
                    )
                    response.raise_for_status()

                    result = response.json()
                    return {
                        'text': result.get('text', '').strip(),
                        'language': result.get('language', 'unknown'),
                        'duration': result.get('duration', 0),
                        'segments': result.get('segments', [])
                    }

        except Exception as e:
            logger.error(f"Error in API transcription: {e}")
            raise


# Singleton instance
whisper_service = WhisperService()
