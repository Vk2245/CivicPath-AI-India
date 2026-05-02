"""test_translate_service.py — Google Cloud Translation tests (Service 6)."""

import pytest
from unittest.mock import patch
from services.translate_service import translate_text


class TestTranslateText:
    @pytest.mark.asyncio
    async def test_returns_demo_when_not_initialized(self):
        with patch("services.translate_service._translate_client", None):
            result = await translate_text("Hello", "hi")
            assert "translated_text" in result
            assert result["target_language"] == "hi"

    @pytest.mark.asyncio
    async def test_unsupported_language_fallback(self):
        with patch("services.translate_service._translate_client", None):
            result = await translate_text("Test", "xx")
            assert result["target_language"] == "en"

    @pytest.mark.asyncio
    async def test_preserves_source_language(self):
        with patch("services.translate_service._translate_client", None):
            result = await translate_text("Test", "fr", source_language="en")
            assert result["source_language"] == "en"
