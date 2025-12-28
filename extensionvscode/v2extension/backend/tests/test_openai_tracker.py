"""Tests for OpenAI token tracking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.openai_tracker import OpenAITracker


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    client = AsyncMock()

    # Mock embeddings response
    embedding_response = MagicMock()
    embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
    embedding_response.usage = MagicMock(
        prompt_tokens=10,
        total_tokens=10
    )

    client.embeddings.create = AsyncMock(return_value=embedding_response)

    # Mock chat completion response
    chat_response = MagicMock()
    chat_response.choices = [
        MagicMock(message=MagicMock(content="Test response"))
    ]
    chat_response.usage = MagicMock(
        prompt_tokens=20,
        completion_tokens=30,
        total_tokens=50
    )

    client.chat.completions.create = AsyncMock(return_value=chat_response)

    return client


@pytest.mark.asyncio
async def test_openai_tracker_create_embedding(mock_openai_client):
    """Test creating embedding with token tracking."""
    with patch('app.core.openai_tracker.AsyncOpenAI', return_value=mock_openai_client):
        tracker = OpenAITracker()

        # Reset usage before test
        tracker.reset_usage()

        embedding = await tracker.create_embedding("test text")

        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

        # Check usage tracking
        usage = tracker.get_current_usage()
        assert usage["prompt_tokens"] == 10
        assert usage["total_tokens"] == 10
        assert usage["model"] == "text-embedding-3-small"


@pytest.mark.asyncio
async def test_openai_tracker_create_embeddings_batch(mock_openai_client):
    """Test creating embeddings in batch."""
    # Mock batch response
    batch_response = MagicMock()
    batch_response.data = [
        MagicMock(embedding=[0.1] * 1536),
        MagicMock(embedding=[0.2] * 1536),
        MagicMock(embedding=[0.3] * 1536),
    ]
    batch_response.usage = MagicMock(
        prompt_tokens=30,
        total_tokens=30
    )

    mock_openai_client.embeddings.create = AsyncMock(return_value=batch_response)

    with patch('app.core.openai_tracker.AsyncOpenAI', return_value=mock_openai_client):
        tracker = OpenAITracker()
        tracker.reset_usage()

        texts = ["text1", "text2", "text3"]
        embeddings = await tracker.create_embeddings_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 1536 for emb in embeddings)

        # Check usage
        usage = tracker.get_current_usage()
        assert usage["prompt_tokens"] == 30
        assert usage["total_tokens"] == 30


@pytest.mark.asyncio
async def test_openai_tracker_chat_completion(mock_openai_client):
    """Test chat completion with token tracking."""
    with patch('app.core.openai_tracker.AsyncOpenAI', return_value=mock_openai_client):
        tracker = OpenAITracker()
        tracker.reset_usage()

        messages = [{"role": "user", "content": "Hello"}]
        response = await tracker.chat_completion(messages)

        assert response == "Test response"

        # Check usage
        usage = tracker.get_current_usage()
        assert usage["prompt_tokens"] == 20
        assert usage["completion_tokens"] == 30
        assert usage["total_tokens"] == 50


@pytest.mark.asyncio
async def test_openai_tracker_accumulates_usage(mock_openai_client):
    """Test that usage accumulates across multiple calls."""
    with patch('app.core.openai_tracker.AsyncOpenAI', return_value=mock_openai_client):
        tracker = OpenAITracker()
        tracker.reset_usage()

        # First embedding
        await tracker.create_embedding("text1")

        # Second embedding
        await tracker.create_embedding("text2")

        # Check accumulated usage
        usage = tracker.get_current_usage()
        assert usage["prompt_tokens"] == 20  # 10 + 10
        assert usage["total_tokens"] == 20

        # Check calls list
        assert len(usage["calls"]) == 2


def test_openai_tracker_estimate_tokens():
    """Test token estimation."""
    text = "This is a test sentence with multiple words."

    estimated = OpenAITracker.estimate_tokens(text)

    # Rough estimate: 1 token ≈ 4 characters
    expected = len(text) // 4
    assert estimated == expected


def test_openai_tracker_reset_usage():
    """Test resetting usage."""
    tracker = OpenAITracker()

    # Manually set some usage
    tracker._update_usage("test-model", 100, 50, 150)

    usage = tracker.get_current_usage()
    assert usage["total_tokens"] == 150

    # Reset
    tracker.reset_usage()

    usage = tracker.get_current_usage()
    assert usage == {}


@pytest.mark.asyncio
async def test_openai_tracker_multiple_models(mock_openai_client):
    """Test tracking usage across different models."""
    with patch('app.core.openai_tracker.AsyncOpenAI', return_value=mock_openai_client):
        tracker = OpenAITracker()
        tracker.reset_usage()

        # Embedding
        await tracker.create_embedding("text", model="text-embedding-3-small")

        # Chat
        await tracker.chat_completion(
            [{"role": "user", "content": "test"}],
            model="gpt-4"
        )

        usage = tracker.get_current_usage()

        # Should track last model used
        assert usage["model"] == "gpt-4"

        # But calls should have both
        assert len(usage["calls"]) == 2
        assert usage["calls"][0]["model"] == "text-embedding-3-small"
        assert usage["calls"][1]["model"] == "gpt-4"
