import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.database import db
from src.api.gemini_service import gemini_service

client = TestClient(app)


def test_root_endpoint():
    """Test root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_api_key():
    """Test API key creation endpoint."""
    response = client.post(
        "/api/v1/auth/create-key",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert "user_id" in data
    assert data["api_key"].startswith("ctx_")
    
    # Store API key for other tests
    pytest.test_api_key = data["api_key"]
    pytest.test_user_id = data["user_id"]


def test_context_retrieve_without_auth():
    """Test context retrieval without API key should fail."""
    response = client.post(
        "/api/v1/context/retrieve",
        json={
            "prompt": "Test prompt",
            "provider": "openai",
            "model": "gpt-4"
        }
    )
    assert response.status_code == 422  # Missing header


def test_context_retrieve_with_auth():
    """Test context retrieval with valid API key."""
    # First create an API key
    key_response = client.post(
        "/api/v1/auth/create-key",
        json={"email": "test2@example.com"}
    )
    api_key = key_response.json()["api_key"]
    
    response = client.post(
        "/api/v1/context/retrieve",
        json={
            "prompt": "Test prompt",
            "provider": "openai",
            "model": "gpt-4"
        },
        headers={"X-API-Key": api_key}
    )
    # Should succeed even if no traces exist yet
    assert response.status_code == 200
    data = response.json()
    assert "enhanced_context" in data
    assert "relevant_traces" in data
    assert "suggestions" in data


def test_store_trace_without_auth():
    """Test trace storage without API key should fail."""
    response = client.post(
        "/api/v1/traces/store",
        json={
            "input": {
                "prompt": "Test prompt",
                "parameters": {}
            },
            "output": {
                "text": "Test response"
            },
            "metadata": {
                "provider": "openai",
                "model": "gpt-4",
                "success": True
            }
        }
    )
    assert response.status_code == 422  # Missing header


def test_store_trace_with_auth():
    """Test trace storage with valid API key."""
    # First create an API key
    key_response = client.post(
        "/api/v1/auth/create-key",
        json={"email": "test3@example.com"}
    )
    api_key = key_response.json()["api_key"]
    
    response = client.post(
        "/api/v1/traces/store",
        json={
            "input": {
                "prompt": "Test prompt",
                "parameters": {}
            },
            "output": {
                "text": "Test response",
                "tokens_used": 100
            },
            "metadata": {
                "provider": "openai",
                "model": "gpt-4",
                "success": True,
                "latency_ms": 500
            }
        },
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data
    assert data["stored"] == True


def test_invalid_api_key():
    """Test endpoints with invalid API key."""
    response = client.post(
        "/api/v1/context/retrieve",
        json={
            "prompt": "Test",
            "provider": "openai",
            "model": "gpt-4"
        },
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401

