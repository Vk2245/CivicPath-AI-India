"""
routers/translate.py — Translation Routes
============================================
Google Service: Google Cloud Translation API
Purpose:        Multilingual election guidance

GOOGLE API CALLS VIA THIS ROUTER:
  - POST /translate → Cloud Translation (text translation)
"""

import logging
from typing import Any

from fastapi import APIRouter, Request

from config import RATE_LIMIT_TRANSLATE
from limiting import limiter
from models import TranslateRequest, TranslateResponse
from services.translate_service import translate_text

logger = logging.getLogger("civicpath.routers.translate")

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("", response_model=TranslateResponse)
@limiter.limit(RATE_LIMIT_TRANSLATE)
async def translate(request: Request, body: TranslateRequest) -> dict[str, Any]:
    """Translate text using Google Cloud Translation API.

    Google Service: Google Cloud Translation API

    Args:
        request: FastAPI request.
        body: Translation request with text and target language.

    Returns:
        Translated text with language information.
    """
    logger.info("Processing translation", extra={"google_service": "Cloud Translation API"})

    # [GOOGLE SERVICE: Cloud Translation] — translate election content
    result = await translate_text(
        text=body.text,
        target_language=body.target_language,
        source_language=body.source_language,
    )

    return {
        "translated_text": result["translated_text"],
        "source_language": result["source_language"],
        "target_language": result["target_language"],
        "google_service": "Google Cloud Translation API",
    }
