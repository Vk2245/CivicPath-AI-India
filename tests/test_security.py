"""test_security.py — Security middleware and sanitization tests."""

from security import sanitize_input, validate_content_length
from tests.conftest import *


class TestSecurityHeaders:
    def test_has_csp_header(self, client):
        response = client.get("/health")
        assert "content-security-policy" in response.headers

    def test_has_hsts_header(self, client):
        response = client.get("/health")
        assert "strict-transport-security" in response.headers

    def test_has_xframe_header(self, client):
        response = client.get("/health")
        assert response.headers["x-frame-options"] == "DENY"

    def test_has_content_type_options(self, client):
        response = client.get("/health")
        assert response.headers["x-content-type-options"] == "nosniff"

    def test_has_referrer_policy(self, client):
        response = client.get("/health")
        assert "referrer-policy" in response.headers

    def test_has_permissions_policy(self, client):
        response = client.get("/health")
        assert "permissions-policy" in response.headers


class TestSanitizeInput:
    def test_removes_html(self):
        assert sanitize_input("<b>bold</b>") == "bold"

    def test_removes_javascript(self):
        assert "javascript" not in sanitize_input("javascript:alert(1)")

    def test_removes_null_bytes(self):
        assert "\x00" not in sanitize_input("hello\x00world")

    def test_preserves_clean_text(self):
        assert sanitize_input("clean text") == "clean text"


class TestContentLength:
    def test_valid_content(self):
        assert validate_content_length(b"small content") is True

    def test_oversized_content(self):
        import pytest

        with pytest.raises(ValueError):
            validate_content_length(b"x" * 20_000_000)
