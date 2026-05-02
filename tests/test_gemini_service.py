"""test_gemini_service.py — Google Gemini service tests (Services 1-3)."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from services.gemini_service import generate_chat_response, detect_myth, generate_embedding


class TestGeminiChat:
    @pytest.mark.asyncio
    async def test_chat_returns_demo_when_not_initialized(self):
        with patch("services.gemini_service._chat_model", None):
            result = await generate_chat_response("How to vote?")
            assert "response" in result
            assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_chat_returns_sources(self):
        with patch("services.gemini_service._chat_model", None):
            result = await generate_chat_response("Registration help")
            assert "sources" in result


class TestMythDetection:
    @pytest.mark.asyncio
    async def test_myth_returns_verdict(self):
        with patch("services.gemini_service._chat_model", None):
            result = await detect_myth("You can only vote on Election Day")
            assert "verdict" in result
            assert "explanation" in result

    @pytest.mark.asyncio
    async def test_myth_returns_sources(self):
        with patch("services.gemini_service._chat_model", None):
            result = await detect_myth("Votes are not counted")
            assert "sources" in result


class TestEmbeddings:
    @pytest.mark.asyncio
    async def test_embedding_returns_vector(self):
        result = await generate_embedding("How to register?")
        assert isinstance(result, list)
        assert len(result) == 768
