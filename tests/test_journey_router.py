"""test_journey_router.py — Journey endpoint tests."""

from tests.conftest import *


class TestJourneyStart:
    def test_start_journey_success(self, client):
        response = client.post(
            "/journey/start",
            json={
                "state": "bihar",
                "is_registered": False,
                "is_first_time": True,
                "election_type": "general",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "journey_id" in data
        assert "steps" in data
        assert len(data["steps"]) >= 5

    def test_start_journey_different_state(self, client):
        response = client.post(
            "/journey/start",
            json={
                "state": "texas",
                "is_registered": True,
                "is_first_time": False,
                "election_type": "primary",
            },
        )
        assert response.status_code == 200

    def test_start_journey_invalid_state(self, client):
        response = client.post("/journey/start", json={"state": "X"})
        assert response.status_code == 422


class TestJourneyGet:
    def test_journey_not_found(self, client):
        response = client.get("/journey/nonexistent-id")
        assert response.status_code == 404
