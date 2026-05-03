"""
conftest.py — CivicPath Test Configuration
=============================================
Fixtures: All 10 Google Services mocked for isolated testing.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_gemini():
    """Mock Google Gemini 1.5 Flash + Vision + Embeddings (Services 1-3)."""
    with (
        patch("services.gemini_service._chat_model") as mock_chat,
        patch("services.gemini_service._vision_model") as mock_vision,
    ):
        mock_response = MagicMock()
        mock_response.text = '{"verdict":"fact","explanation":"This is accurate.","confidence":0.9,"sources":["vote.gov"]}'
        mock_chat.generate_content_async = AsyncMock(return_value=mock_response)
        mock_vision.generate_content_async = AsyncMock(return_value=mock_response)
        yield {"chat": mock_chat, "vision": mock_vision}


@pytest.fixture
def mock_speech():
    """Mock Google Cloud Speech-to-Text + Text-to-Speech (Services 4-5)."""
    with (
        patch("services.speech_service._stt_client") as stt,
        patch("services.speech_service._tts_client") as tts,
    ):
        yield {"stt": stt, "tts": tts}


@pytest.fixture
def mock_translate():
    """Mock Google Cloud Translation API (Service 6)."""
    with patch("services.translate_service._translate_client") as t:
        t.translate.return_value = {"translatedText": "Translated", "detectedSourceLanguage": "en"}
        yield t


@pytest.fixture
def mock_maps():
    """Mock Google Maps Places API (Service 7)."""
    with patch("services.maps_service._maps_client") as m:
        m.places_nearby.return_value = {"results": []}
        yield m


@pytest.fixture
def mock_recaptcha():
    """Mock Google reCAPTCHA v3 (Service 8)."""
    with patch("services.recaptcha_service._http_client") as h:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"success": True, "score": 0.9}
        h.post = AsyncMock(return_value=mock_resp)
        yield h


@pytest.fixture
def mock_analytics():
    """Mock Google Analytics 4 (Service 9)."""
    with patch("services.analytics_service._http_client") as h:
        h.post = AsyncMock(return_value=MagicMock(status_code=204))
        yield h


@pytest.fixture
def mock_firebase():
    """Mock Firebase database operations."""
    with patch("services.firebase_service._firebase_client") as s:
        yield s
