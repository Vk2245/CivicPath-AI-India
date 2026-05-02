"""test_health_router.py — Health and Google Services endpoint tests."""

from tests.conftest import *


class TestHealthEndpoint:
    def test_health_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["google_services_count"] == 10

    def test_health_has_version(self, client):
        response = client.get("/health")
        assert "version" in response.json()

    def test_health_has_timestamp(self, client):
        response = client.get("/health")
        assert "timestamp" in response.json()


class TestGoogleServicesEndpoint:
    def test_lists_all_services(self, client):
        response = client.get("/google-services")
        assert response.status_code == 200
        data = response.json()
        assert data["total_google_services"] == 10

    def test_has_service_details(self, client):
        response = client.get("/google-services")
        services = response.json()["services"]
        assert "gemini_flash" in services
        assert "google_fonts" in services

    def test_each_service_has_required_fields(self, client):
        response = client.get("/google-services")
        for key, svc in response.json()["services"].items():
            assert "name" in svc
            assert "purpose" in svc
            assert "sdk_package" in svc
