"""
OpenAI Token Tracker - Tracking de uso de tokens de OpenAI.

Wrappea las llamadas a OpenAI para trackear tokens consumidos.
"""

from typing import Optional, Dict, Any, List
from contextvars import ContextVar
from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletion

from app.core.config import settings


# Context var para almacenar usage del request actual
_openai_usage: ContextVar[Dict[str, Any]] = ContextVar('openai_usage', default={})


class OpenAITracker:
    """
    Wrapper de OpenAI que trackea el uso de tokens.

    Usage:
        tracker = OpenAITracker()
        embedding = await tracker.create_embedding("text")
        usage = tracker.get_current_usage()
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    def _update_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int = 0,
        total_tokens: Optional[int] = None
    ) -> None:
        """Actualizar usage en context var."""
        current_usage = _openai_usage.get({})

        if not total_tokens:
            total_tokens = prompt_tokens + completion_tokens

        # Acumular tokens
        current_usage["prompt_tokens"] = current_usage.get("prompt_tokens", 0) + prompt_tokens
        current_usage["completion_tokens"] = current_usage.get("completion_tokens", 0) + completion_tokens
        current_usage["total_tokens"] = current_usage.get("total_tokens", 0) + total_tokens
        current_usage["model"] = model  # Last model used

        # Almacenar lista de llamadas
        if "calls" not in current_usage:
            current_usage["calls"] = []

        current_usage["calls"].append({
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        })

        _openai_usage.set(current_usage)

    async def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Crear embedding con tracking de tokens.

        Args:
            text: Texto a embedear
            model: Modelo de OpenAI

        Returns:
            Vector de embedding
        """
        response: CreateEmbeddingResponse = await self.client.embeddings.create(
            model=model,
            input=text
        )

        # Trackear uso
        usage = response.usage
        self._update_usage(
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=0,
            total_tokens=usage.total_tokens
        )

        return response.data[0].embedding

    async def create_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """
        Crear embeddings en batch (más eficiente).

        Args:
            texts: Lista de textos
            model: Modelo de OpenAI

        Returns:
            Lista de vectores de embedding
        """
        response: CreateEmbeddingResponse = await self.client.embeddings.create(
            model=model,
            input=texts
        )

        # Trackear uso
        usage = response.usage
        self._update_usage(
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=0,
            total_tokens=usage.total_tokens
        )

        return [item.embedding for item in response.data]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat completion con tracking de tokens.

        Args:
            messages: Lista de mensajes
            model: Modelo de OpenAI
            temperature: Temperature para generación
            max_tokens: Máximo de tokens a generar

        Returns:
            Response text
        """
        response: ChatCompletion = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Trackear uso
        usage = response.usage
        if usage:
            self._update_usage(
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )

        return response.choices[0].message.content

    @staticmethod
    def get_current_usage() -> Dict[str, Any]:
        """Obtener usage del request actual."""
        return _openai_usage.get({})

    @staticmethod
    def reset_usage() -> None:
        """Reset usage (llamar al inicio de cada request)."""
        _openai_usage.set({})

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimar tokens sin llamar a OpenAI.

        Aproximación: 1 token ≈ 4 caracteres en inglés
        """
        return len(text) // 4


# Dependency para FastAPI
async def get_openai_tracker() -> OpenAITracker:
    """Get OpenAI tracker instance."""
    return OpenAITracker()


# Middleware helper para resetear usage
def reset_openai_usage():
    """Reset OpenAI usage tracking (llamar al inicio de request)."""
    OpenAITracker.reset_usage()


def get_openai_usage() -> Dict[str, Any]:
    """Get current OpenAI usage."""
    return OpenAITracker.get_current_usage()
