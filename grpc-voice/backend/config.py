from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # gRPC
    grpc_port: int = 50051
    grpc_web_port: int = 8080

    # Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_api_url: str | None = None

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "transcriptions"
    rabbitmq_queue: str = "transcription_queue"
    rabbitmq_routing_key: str = "transcription.new"

    # FastAPI
    api_port: int = 8001

    # Audio
    max_audio_size_mb: int = 25
    temp_audio_dir: str = "./temp_audio"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
