"""test_reminder_router.py — Reminder subscription endpoint tests."""

from tests.conftest import *


class TestReminderSubscribe:
    def test_subscribe_success(self, client):
        response = client.post("/reminders/subscribe", json={
            "email": "voter@example.com", "name": "Jane Doe",
            "recaptcha_token": "valid_token_1234567890"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_subscribe_invalid_email(self, client):
        response = client.post("/reminders/subscribe", json={
            "email": "notvalid", "name": "Jane", "recaptcha_token": "a" * 20
        })
        assert response.status_code == 422

    def test_subscribe_missing_token(self, client):
        response = client.post("/reminders/subscribe", json={
            "email": "test@test.com", "name": "Jane"
        })
        assert response.status_code == 422
