"""Tests for FastAPI main application."""

from fastapi.testclient import TestClient
import pytest


def test_health_check():
    """Test health check endpoint."""
    from src.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint returns API information."""
    from src.main import app
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Krepsys API"
    assert "version" in data
    assert "docs" in data


def test_cors_headers():
    """Test that CORS headers are present."""
    from src.main import app
    
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:18300",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    # CORS middleware should add these headers
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_app_title_and_version():
    """Test that app has correct title and version."""
    from src.main import app
    
    assert app.title == "Krepsys API"
    assert app.version == "0.1.0"
    assert "newsletter reader" in app.description.lower()
