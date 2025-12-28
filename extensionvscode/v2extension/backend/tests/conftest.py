"""Pytest configuration and fixtures."""

import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings


# Override database URL for tests
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "data": [
            {
                "embedding": [0.1] * 1536,
                "index": 0
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    }
