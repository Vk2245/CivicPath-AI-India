"""
recaptcha_service.py — Google reCAPTCHA v3 Integration
========================================================
Google Service: Google reCAPTCHA v3 API
SDK Package:    httpx (direct REST call to Google reCAPTCHA API)
Purpose:        Bot protection on reminder subscription endpoint
Inputs:         reCAPTCHA token from frontend
Outputs:        Verification result with score
Deps:           httpx==0.28.1

Challenge Alignment: Bot protection ensures the Election Process Education
platform's reminder system is not abused by automated bots.

GOOGLE API CALLS IN THIS MODULE:
  - verify_recaptcha(): Calls Google reCAPTCHA v3 to verify user is human
"""

import logging
from typing import Any

import httpx

from config import MIN_RECAPTCHA_SCORE, RECAPTCHA_VERIFY_URL, get_settings
from demo_data import DEMO_DATA
from exceptions import RecaptchaError

logger = logging.getLogger("civicpath.recaptcha")

# ═══ GOOGLE SERVICE: reCAPTCHA v3 ═══
# SDK: httpx (REST call to Google reCAPTCHA API)
# Docs: https://developers.google.com/recaptcha/docs/v3

_http_client: httpx.AsyncClient | None = None


async def init_recaptcha_client(http_client: httpx.AsyncClient) -> None:
    """Initialize reCAPTCHA service with shared HTTP client.

    Google Service: Google reCAPTCHA v3 API
    """
    global _http_client
    _http_client = http_client
    logger.info(
        "Google reCAPTCHA v3 service initialized",
        extra={"google_service": "Google reCAPTCHA v3 API"},
    )


async def verify_recaptcha(token: str) -> dict[str, Any]:
    """Verify a reCAPTCHA v3 token using Google reCAPTCHA API.

    Google Service Used: Google reCAPTCHA v3 API
    SDK Call: POST https://www.google.com/recaptcha/api/siteverify

    Args:
        token: reCAPTCHA token from frontend.

    Returns:
        Dictionary with success status and score.

    Raises:
        RecaptchaError: If verification fails.
    """
    logger.info(
        "Calling Google reCAPTCHA v3 API",
        extra={"function": "verify_recaptcha", "google_service": "reCAPTCHA v3"},
    )

    settings = get_settings()
    if not settings.RECAPTCHA_SECRET_KEY:
        logger.warning("RECAPTCHA_SECRET_KEY not set — demo mode")
        return DEMO_DATA["recaptcha"]

    if _http_client is None:
        logger.warning("HTTP client not initialized — demo mode")
        return DEMO_DATA["recaptcha"]

    try:
        # [GOOGLE SERVICE: reCAPTCHA v3] — verify token with Google
        response = await _http_client.post(
            RECAPTCHA_VERIFY_URL,
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": token,
            },
        )
        result = response.json()

        success = result.get("success", False)
        score = result.get("score", 0.0)

        if success and score >= MIN_RECAPTCHA_SCORE:
            logger.info(
                "Google reCAPTCHA v3 verification passed",
                extra={"google_service": "reCAPTCHA v3", "score": score},
            )
            return {"success": True, "score": score, "action": result.get("action", "")}

        logger.warning(
            "reCAPTCHA verification failed or low score",
            extra={"score": score, "google_service": "reCAPTCHA v3"},
        )
        raise RecaptchaError(
            message="reCAPTCHA verification failed",
            detail={"score": score, "success": success},
        )
    except RecaptchaError:
        raise
    except Exception as exc:
        logger.error(
            "Google reCAPTCHA v3 API call failed",
            extra={"error": str(exc), "google_service": "reCAPTCHA v3"},
        )
        return DEMO_DATA["recaptcha"]
