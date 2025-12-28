"""Tests for rate limiting system."""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.rate_limiter import (
    RateLimiter,
    TokenBucket,
    RateLimitConfig,
    RateLimitResult,
)


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis_mock = AsyncMock()

    # Mock eval to simulate Token Bucket behavior
    async def mock_eval(script, num_keys, *args):
        # Simple simulation: always allow first request
        return [1, 99, 1]  # allowed=1, tokens_available=99, tokens_consumed=1

    redis_mock.eval = AsyncMock(side_effect=mock_eval)
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock()
    redis_mock.get = AsyncMock(return_value=b"1")
    redis_mock.delete = AsyncMock()
    redis_mock.hmget = AsyncMock(return_value=[100.0, time.time()])

    return redis_mock


@pytest.fixture
def rate_limiter(mock_redis):
    """Create a RateLimiter instance with mock Redis."""
    return RateLimiter(mock_redis)


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit(rate_limiter, mock_redis):
    """Test that requests within limit are allowed."""
    result = await rate_limiter.check_limit(
        user_id="test_user",
        action="api_call",
        tokens=1
    )

    assert result.allowed is True
    assert result.tokens_requested == 1
    assert result.tokens_consumed == 1


@pytest.mark.asyncio
async def test_rate_limiter_blocks_over_limit(mock_redis):
    """Test that requests over limit are blocked."""
    # Mock to simulate no tokens available
    async def mock_eval_blocked(script, num_keys, *args):
        return [0, 0, 0, 30.0]  # allowed=0, tokens=0, consumed=0, retry_after=30

    mock_redis.eval = AsyncMock(side_effect=mock_eval_blocked)
    mock_redis.get = AsyncMock(return_value=b"100")

    limiter = RateLimiter(mock_redis)

    result = await limiter.check_limit(
        user_id="test_user",
        action="api_call",
        tokens=1
    )

    assert result.allowed is False
    assert result.retry_after_seconds is not None
    assert result.retry_after_seconds > 0


@pytest.mark.asyncio
async def test_rate_limiter_configs(rate_limiter):
    """Test that different actions have different configs."""
    # API call config
    api_result = await rate_limiter.check_limit(
        user_id="test_user",
        action="api_call"
    )
    assert api_result.max_requests == 100

    # Embedding generation has stricter limits
    config = rate_limiter.configs["embedding_generation"]
    assert config.max_requests == 20
    assert config.window_seconds == 60


@pytest.mark.asyncio
async def test_token_bucket_consume(mock_redis):
    """Test TokenBucket consume method."""
    bucket = TokenBucket(mock_redis)
    config = RateLimitConfig(
        max_requests=100,
        window_seconds=60,
        burst_multiplier=1.5
    )

    result = await bucket.consume(
        key="test_key",
        tokens=1,
        config=config
    )

    assert isinstance(result, RateLimitResult)
    assert result.allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_reset(rate_limiter):
    """Test resetting user limits."""
    await rate_limiter.reset_user_limits("test_user", "api_call")

    # Verify delete was called
    rate_limiter.bucket.redis.delete.assert_called()


@pytest.mark.asyncio
async def test_rate_limiter_get_status(rate_limiter, mock_redis):
    """Test getting user status."""
    mock_redis.hmget = AsyncMock(return_value=[b"50.0", str(time.time()).encode()])
    mock_redis.get = AsyncMock(return_value=b"10")

    status = await rate_limiter.get_user_status("test_user")

    assert "api_call" in status
    assert "embedding_generation" in status


@pytest.mark.asyncio
async def test_rate_limiter_custom_config(rate_limiter):
    """Test using custom rate limit config."""
    custom_config = RateLimitConfig(
        max_requests=5,
        window_seconds=10,
        burst_multiplier=1.0
    )

    result = await rate_limiter.check_limit(
        user_id="test_user",
        action="custom_action",
        tokens=1,
        custom_config=custom_config
    )

    assert result.allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_burst_support(rate_limiter):
    """Test that burst multiplier works."""
    config = rate_limiter.configs["api_call"]

    # Max requests is 100, burst multiplier is 1.5
    # So effective burst limit is 150
    assert config.max_requests == 100
    assert config.burst_multiplier == 1.5

    effective_burst = int(config.max_requests * config.burst_multiplier)
    assert effective_burst == 150


@pytest.mark.asyncio
async def test_rate_limiter_error_handling(mock_redis):
    """Test that rate limiter fails open on Redis errors."""
    # Simulate Redis error
    mock_redis.eval = AsyncMock(side_effect=Exception("Redis connection failed"))

    limiter = RateLimiter(mock_redis)

    result = await limiter.check_limit(
        user_id="test_user",
        action="api_call",
        tokens=1
    )

    # Should fail open (allow the request)
    assert result.allowed is True
    assert result.tokens_consumed == 0
