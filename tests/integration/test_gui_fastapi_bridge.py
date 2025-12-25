"""
Integration tests for FastAPI GUI bridge.

Tests the REST API endpoints connecting the React frontend to CodeSentinel backend.
"""

import json
import pytest
from fastapi.testclient import TestClient

# Add src to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sentinel.api.fastapi_bridge import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test the /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Health endpoint should return required fields."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "api_version" in data
        assert data["status"] == "healthy"


class TestConfigEndpoint:
    """Test the /api/config endpoint."""

    def test_config_returns_200(self, client):
        """Config endpoint should return 200 OK."""
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_config_returns_config_object(self, client):
        """Config endpoint should return a valid config object."""
        response = client.get("/api/config")
        data = response.json()
        
        # Should have config structure
        assert isinstance(data, dict)
        # Config should include some expected fields
        assert "scan_defaults" in data or len(data) > 0


class TestScanEndpoints:
    """Test scan-related endpoints."""

    def test_list_scans_returns_200(self, client):
        """GET /api/scans should return 200 OK."""
        response = client.get("/api/scans")
        assert response.status_code == 200

    def test_list_scans_returns_list(self, client):
        """GET /api/scans should return a list."""
        response = client.get("/api/scans")
        data = response.json()
        assert isinstance(data, list)

    def test_scan_not_found_returns_404(self, client):
        """GET /api/scans/{id} with non-existent ID should return 404."""
        response = client.get("/api/scans/nonexistent-id")
        assert response.status_code == 404


class TestFindingsEndpoints:
    """Test finding-related endpoints."""

    def test_list_findings_returns_200(self, client):
        """GET /api/findings should return 200 OK."""
        response = client.get("/api/findings")
        assert response.status_code == 200

    def test_list_findings_returns_list(self, client):
        """GET /api/findings should return a list."""
        response = client.get("/api/findings")
        data = response.json()
        assert isinstance(data, list)

    def test_finding_not_found_returns_404(self, client):
        """GET /api/findings/{id} with non-existent ID should return 404."""
        response = client.get("/api/findings/nonexistent-finding")
        assert response.status_code == 404


class TestProjectEndpoints:
    """Test project history endpoints."""

    def test_list_projects_returns_200(self, client):
        """GET /api/projects should return 200 OK."""
        response = client.get("/api/projects")
        assert response.status_code == 200

    def test_list_projects_returns_list(self, client):
        """GET /api/projects should return a list."""
        response = client.get("/api/projects")
        data = response.json()
        assert isinstance(data, list)


class TestCORSHeaders:
    """Test CORS middleware configuration."""

    def test_cors_headers_present(self, client):
        """Response should include CORS headers."""
        response = client.get("/health")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or \
               "Access-Control-Allow-Origin" in response.headers


class TestAPIDocumentation:
    """Test that API documentation is available."""

    def test_openapi_json_available(self, client):
        """OpenAPI spec should be available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_swagger_docs_available(self, client):
        """Swagger UI should be available."""
        response = client.get("/docs")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
