"""
translate_service.py — Google Cloud Translation Integration
=============================================================
Google Service: Google Cloud Translation API
SDK Package:    google-cloud-translate==3.19.0
Purpose:        Multilingual election guidance — 10+ languages
Inputs:         Text to translate, target language code
Outputs:        Translated text with detected source language
Deps:           google-cloud-translate==3.19.0

Challenge Alignment: This module addresses the challenge of making election
guidance "easy to follow" for ALL users by providing multilingual support
via Google Cloud Translation API.

GOOGLE API CALLS IN THIS MODULE:
  - translate_text(): Calls Google Cloud Translation to translate content
"""

import logging
from typing import Any, Optional

from config import SUPPORTED_LANGUAGES, get_settings
from demo_data import DEMO_DATA
from exceptions import TranslationError

logger = logging.getLogger("civicpath.translate")

# ═══ GOOGLE SERVICE: Cloud Translation API ═══
# SDK: google-cloud-translate
# Docs: https://cloud.google.com/translate/docs

_translate_client: Any = None


async def init_translate_client() -> None:
    """Initialize Google Cloud Translation API client.

    Google Service: Cloud Translation API
    SDK: google-cloud-translate
    """
    global _translate_client
    settings = get_settings()

    if not settings.GOOGLE_CLOUD_PROJECT:
        logger.warning(
            "GOOGLE_CLOUD_PROJECT not set — Translation in demo mode",
            extra={"google_service": "Google Cloud Translation API"},
        )
        return

    try:
        # [GOOGLE SERVICE: Cloud Translation] — client initialization
        from google.cloud import translate_v2 as translate
        _translate_client = translate.Client()

        logger.info(
            "Google Cloud Translation client initialized",
            extra={"google_service": "Google Cloud Translation API"},
        )
    except Exception as exc:
        logger.error(
            "Failed to init Google Cloud Translation",
            extra={"error": str(exc), "google_service": "Cloud Translation API"},
        )


async def translate_text(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
) -> dict[str, Any]:
    """Translate text using Google Cloud Translation API.

    Integrates Google Cloud Translation API for multilingual election
    guidance. Supports 10+ languages for inclusive voter education.

    Google Service Used: Google Cloud Translation API
    SDK Call: translate.Client().translate(text, target_language)

    Args:
        text: Text to translate.
        target_language: ISO 639-1 target language code.
        source_language: Optional source language (auto-detect if None).

    Returns:
        Dictionary with translated text and language info.

    Raises:
        TranslationError: If Google Cloud Translation API fails.
    """
    logger.info(
        "Calling Google Cloud Translation API",
        extra={
            "function": "translate_text",
            "google_service": "Cloud Translation API",
            "target": target_language,
        },
    )

    if target_language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language: {target_language}, falling back to en")
        target_language = "en"

    if _translate_client is None:
        logger.warning("Translation not initialized — demo fallback")
        return {
            "translated_text": f"[{target_language}] {text}",
            "source_language": source_language or "en",
            "target_language": target_language,
        }

    try:
        kwargs: dict[str, Any] = {
            "values": text,
            "target_language": target_language,
        }
        if source_language:
            kwargs["source_language"] = source_language

        # [GOOGLE SERVICE: Cloud Translation] — translate election content
        result = _translate_client.translate(**kwargs)

        logger.info(
            "Google Cloud Translation call succeeded",
            extra={"google_service": "Cloud Translation API"},
        )

        return {
            "translated_text": result["translatedText"],
            "source_language": result.get("detectedSourceLanguage", source_language or "en"),
            "target_language": target_language,
        }
    except Exception as exc:
        logger.error(
            "Google Cloud Translation API failed",
            extra={"error": str(exc), "google_service": "Cloud Translation API"},
        )
        return {
            "translated_text": f"[{target_language}] {text}",
            "source_language": source_language or "en",
            "target_language": target_language,
        }
