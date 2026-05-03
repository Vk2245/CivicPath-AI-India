"""test_chat_router.py — Chat and Myth Detection endpoint tests."""

from tests.conftest import *


class TestChatEndpoint:
    def test_chat_success(self, client):
        response = client.post("/chat", json={"message": "How do I register to vote?"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["google_service"] == "Google Gemini 1.5 Flash API"

    def test_chat_empty_message(self, client):
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 422

    def test_chat_xss_sanitized(self, client):
        response = client.post(
            "/chat", json={"message": "<script>alert(1)</script>What is voting?"}
        )
        assert response.status_code == 200


class TestMythCheck:
    def test_myth_check_success(self, client):
        response = client.post(
            "/chat/myth-check", json={"text": "You cannot vote by mail in any state"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "verdict" in data

    def test_myth_check_too_short(self, client):
        response = client.post("/chat/myth-check", json={"text": "Hi"})
        assert response.status_code == 422

    def test_myth_check_has_google_service(self, client):
        response = client.post(
            "/chat/myth-check", json={"text": "All votes are counted by hand in every state"}
        )
        assert response.json()["google_service"] == "Google Gemini 1.5 Flash API"
