"""test_speech_service.py — Google Cloud Speech tests (Services 4-5)."""

from unittest.mock import patch

import pytest

from services.speech_service import synthesize_speech, transcribe_audio


class TestTranscribeAudio:
    @pytest.mark.asyncio
    async def test_returns_demo_when_not_initialized(self):
        with patch("services.speech_service._stt_client", None):
            result = await transcribe_audio(b"fake_audio")
            assert "transcript" in result

    @pytest.mark.asyncio
    async def test_returns_confidence(self):
        with patch("services.speech_service._stt_client", None):
            result = await transcribe_audio(b"audio_data")
            assert "confidence" in result


class TestSynthesizeSpeech:
    @pytest.mark.asyncio
    async def test_returns_demo_when_not_initialized(self):
        with patch("services.speech_service._tts_client", None):
            result = await synthesize_speech("Hello voter")
            assert "message" in result

    @pytest.mark.asyncio
    async def test_accepts_language_param(self):
        with patch("services.speech_service._tts_client", None):
            result = await synthesize_speech("Hola", language="es-US")
            assert result is not None
