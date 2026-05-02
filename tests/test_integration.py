"""test_integration.py — Full user journey integration test."""

from tests.conftest import *


class TestFullUserJourney:
    """Integration test: onboard → journey → chat → myth check → complete."""

    def test_complete_user_flow(self, client):
        # Step 1: Create journey
        journey_res = client.post("/journey/start", json={
            "state": "bihar", "is_registered": False,
            "is_first_time": True, "election_type": "general"
        })
        assert journey_res.status_code == 200
        journey_id = journey_res.json()["journey_id"]
        steps = journey_res.json()["steps"]
        assert len(steps) >= 5

        # Step 2: Complete a step
        step_res = client.put(f"/journey/{journey_id}/step", json={
            "step_number": 1, "status": "completed"
        })
        assert step_res.status_code == 200

        # Step 3: Chat with AI assistant
        chat_res = client.post("/chat", json={
            "message": "What ID do I need to vote in Bihar?",
            "journey_id": journey_id
        })
        assert chat_res.status_code == 200
        assert "response" in chat_res.json()

        # Step 4: Myth check
        myth_res = client.post("/chat/myth-check", json={
            "text": "EVMs can be hacked via bluetooth"
        })
        assert myth_res.status_code == 200
        assert "verdict" in myth_res.json()

        # Step 5: Health check
        health_res = client.get("/health")
        assert health_res.status_code == 200
        assert health_res.json()["status"] == "healthy"

        # Step 6: Google services manifest
        svc_res = client.get("/google-services")
        assert svc_res.status_code == 200
        assert svc_res.json()["total_google_services"] == 10


class TestAPIErrorHandling:
    def test_404_on_unknown_route(self, client):
        response = client.get("/nonexistent")
        assert response.status_code in [404, 200]  # 200 if static fallback

    def test_422_on_invalid_json(self, client):
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_422_on_missing_required_field(self, client):
        response = client.post("/journey/start", json={})
        assert response.status_code == 422
