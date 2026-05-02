"""
routers/reminders.py — Deadline Reminder Routes
==================================================
Google Service: Google reCAPTCHA v3 API
Purpose:        Bot-protected reminder subscription endpoint

GOOGLE API CALLS VIA THIS ROUTER:
  - POST /reminders/subscribe → reCAPTCHA v3 (bot protection)
"""

import logging
from typing import Any

from fastapi import APIRouter, Request

from config import RATE_LIMIT_REMINDERS
from limiting import limiter
from models import ReminderSubscribeRequest, ReminderSubscribeResponse
from services import firebase_service
from services.recaptcha_service import verify_recaptcha
from services.reminder_service import send_reminder_email

logger = logging.getLogger("civicpath.routers.reminders")

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("/subscribe", response_model=ReminderSubscribeResponse)
@limiter.limit(RATE_LIMIT_REMINDERS)
async def subscribe(request: Request, body: ReminderSubscribeRequest) -> dict[str, Any]:
    """Subscribe to election deadline reminders.

    Protected by Google reCAPTCHA v3 to prevent bot abuse.

    Google Service: Google reCAPTCHA v3 API

    Args:
        request: FastAPI request.
        body: Subscription data with reCAPTCHA token.

    Returns:
        Subscription confirmation.
    """
    logger.info("Processing reminder subscription", extra={"google_service": "reCAPTCHA v3"})

    # [GOOGLE SERVICE: reCAPTCHA v3] — verify subscriber is human
    await verify_recaptcha(body.recaptcha_token)

    # Save reminder subscription
    await firebase_service.create_reminder({
        "email": body.email,
        "name": body.name,
        "journey_id": body.journey_id,
    })

    # Send confirmation email
    await send_reminder_email(body.email, body.name, body.journey_id)

    return {
        "success": True,
        "message": f"Reminder subscription confirmed for {body.email}",
        "google_service": "Google reCAPTCHA v3 API",
    }
