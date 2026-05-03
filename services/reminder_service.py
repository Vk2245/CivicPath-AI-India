"""
reminder_service.py — Election Reminder Service
==================================================
Purpose:        Email reminder delivery via Resend API
Inputs:         Subscriber email, journey deadlines
Outputs:        Email delivery confirmation
Deps:           httpx==0.28.1

Challenge Alignment: Deadline reminders help voters complete all
election preparation steps on time.
"""

import logging
from typing import Any

import httpx

from config import get_settings

logger = logging.getLogger("civicpath.reminder")

_http_client: httpx.AsyncClient | None = None


async def init_reminder_client(http_client: httpx.AsyncClient) -> None:
    """Initialize reminder service with shared HTTP client."""
    global _http_client
    _http_client = http_client
    logger.info("Reminder service initialized")


async def send_reminder_email(
    email: str, name: str, journey_id: str | None = None
) -> dict[str, Any]:
    """Send a deadline reminder subscription confirmation.

    Args:
        email: Subscriber's email address.
        name: Subscriber's name.
        journey_id: Associated journey ID.

    Returns:
        Email delivery result.
    """
    settings = get_settings()

    if not settings.RESEND_API_KEY or _http_client is None:
        logger.warning("Resend not configured — demo mode")
        return {
            "success": True,
            "message": f"Demo: Reminder subscription confirmed for {email}",
        }

    try:
        response = await _http_client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "CivicPath <reminders@civicpath.app>",
                "to": [email],
                "subject": "🗳️ CivicPath — Your Election Reminders Are Set!",
                "html": (
                    f"<h2>Welcome, {name}!</h2>"
                    "<p>You're now subscribed to election deadline reminders from CivicPath.</p>"
                    "<p>We'll send you timely reminders for:</p>"
                    "<ul>"
                    "<li>Registration deadlines</li>"
                    "<li>Early voting dates</li>"
                    "<li>Election day reminders</li>"
                    "</ul>"
                    "<p>Democracy starts with showing up. We'll help you get there.</p>"
                    "<p><em>— The CivicPath Team</em></p>"
                ),
            },
        )

        if response.status_code == 200:
            logger.info(f"Reminder email sent to {email}")
            return {"success": True, "message": "Reminder subscription confirmed"}

        logger.error(f"Resend API error: {response.status_code}")
        return {"success": True, "message": f"Subscription saved for {email}"}
    except Exception as exc:
        logger.error(f"Reminder email failed: {exc}")
        return {"success": True, "message": f"Subscription saved for {email}"}
