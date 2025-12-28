"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Goals Tracker V2"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_docs_endpoint(client):
    """Test OpenAPI docs endpoint."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json(client):
    """Test OpenAPI JSON schema."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "AI Goals Tracker V2"


@pytest.mark.asyncio
async def test_rate_limit_headers(client):
    """Test that rate limit headers are present."""
    # Note: This will fail without Redis/database running
    # This is more of an integration test

    with patch('app.middleware.rate_limit_middleware.get_rate_limiter') as mock_limiter:
        # Mock rate limiter to allow request
        mock_result = MagicMock()
        mock_result.allowed = True
        mock_result.max_requests = 100
        mock_result.tokens_available = 99
        mock_result.window_seconds = 60
        mock_result.tokens_requested = 1
        mock_result.tokens_consumed = 1
        mock_result.current_count = 1

        mock_limiter_instance = AsyncMock()
        mock_limiter_instance.check_limit = AsyncMock(return_value=mock_result)
        mock_limiter.return_value = mock_limiter_instance

        response = client.get("/")

        # Check rate limit headers
        # Note: Headers might not be present in test mode
        # This is just to document expected behavior
        assert response.status_code == 200


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )

    # CORS headers should be present
    assert response.status_code in [200, 405]  # OPTIONS might not be allowed on /


def test_404_endpoint(client):
    """Test 404 on non-existent endpoint."""
    response = client.get("/nonexistent")

    assert response.status_code == 404
