"""test_models.py — Pydantic model validation tests."""

import pytest
from models import (
    ChatRequest, JourneyStartRequest, MythCheckRequest,
    ReminderSubscribeRequest, TranslateRequest, strip_html_tags,
)


class TestStripHtmlTags:
    def test_removes_script_tags(self):
        assert strip_html_tags("<script>alert('xss')</script>hello") == "alert('xss')hello"

    def test_removes_html_tags(self):
        assert strip_html_tags("<b>bold</b>") == "bold"

    def test_preserves_clean_text(self):
        assert strip_html_tags("clean text") == "clean text"


class TestJourneyStartRequest:
    def test_state_sanitization(self):
        req = JourneyStartRequest(state="Bihar")
        assert req.state == "bihar"

    def test_sanitizes_state(self):
        req = JourneyStartRequest(state="<script>CA</script>")
        assert "<script>" not in req.state

    def test_rejects_short_state(self):
        with pytest.raises(Exception):
            JourneyStartRequest(state="X")


class TestChatRequest:
    def test_valid_message(self):
        req = ChatRequest(message="How do I register to vote?")
        assert req.message == "How do I register to vote?"

    def test_sanitizes_xss(self):
        req = ChatRequest(message="<img onerror=alert(1)>question")
        assert "<img" not in req.message

    def test_rejects_empty(self):
        with pytest.raises(Exception):
            ChatRequest(message="")


class TestMythCheckRequest:
    def test_valid_text(self):
        req = MythCheckRequest(text="You cannot vote by mail")
        assert req.text == "You cannot vote by mail"

    def test_rejects_short(self):
        with pytest.raises(Exception):
            MythCheckRequest(text="Hi")


class TestReminderSubscribeRequest:
    def test_valid_email(self):
        req = ReminderSubscribeRequest(
            email="test@example.com", name="John", recaptcha_token="a" * 20
        )
        assert req.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(Exception):
            ReminderSubscribeRequest(
                email="notanemail", name="John", recaptcha_token="a" * 20
            )


class TestTranslateRequest:
    def test_valid_request(self):
        req = TranslateRequest(text="Hello", target_language="es")
        assert req.target_language == "es"
