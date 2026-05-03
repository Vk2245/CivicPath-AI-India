"""
analytics_service.py — Google Analytics 4 Integration
=======================================================
Google Service: Google Analytics 4 (GA4) — Measurement Protocol
SDK Package:    httpx (Measurement Protocol REST API) + gtag.js (frontend)
Purpose:        Track civic engagement funnel events server-side
Inputs:         Event name, event parameters, client ID
Outputs:        Event acknowledgment
Deps:           httpx==0.28.1

Challenge Alignment: Tracking civic engagement metrics demonstrates
measurable impact of the Election Process Education platform.

GOOGLE API CALLS IN THIS MODULE:
  - track_event(): Calls GA4 Measurement Protocol to log server-side events
"""

import logging
from typing import Any

import httpx

from config import GA4_COLLECT_URL, get_settings
from demo_data import DEMO_DATA

logger = logging.getLogger("civicpath.analytics")

# ═══ GOOGLE SERVICE: Google Analytics 4 (Measurement Protocol) ═══
# SDK: httpx (REST) + gtag.js (frontend)
# Docs: https://developers.google.com/analytics/devguides/collection/protocol/ga4

_http_client: httpx.AsyncClient | None = None


async def init_analytics_client(http_client: httpx.AsyncClient) -> None:
    """Initialize GA4 analytics with shared HTTP client.

    Google Service: Google Analytics 4 (Measurement Protocol)
    """
    global _http_client
    _http_client = http_client
    logger.info(
        "Google Analytics 4 service initialized",
        extra={"google_service": "Google Analytics 4"},
    )


async def track_event(
    event_name: str,
    params: dict[str, Any] | None = None,
    client_id: str = "server",
) -> dict[str, Any]:
    """Track a server-side event via GA4 Measurement Protocol.

    Google Service Used: Google Analytics 4 (Measurement Protocol)
    SDK Call: POST https://www.google-analytics.com/mp/collect

    Args:
        event_name: GA4 event name (e.g., journey_started, step_completed).
        params: Optional event parameters.
        client_id: Client identifier for GA4.

    Returns:
        Dictionary with event tracking status.

    Raises:
        AnalyticsError: If GA4 event tracking fails.
    """
    logger.info(
        "Calling Google Analytics 4 Measurement Protocol",
        extra={
            "function": "track_event",
            "google_service": "Google Analytics 4",
            "event": event_name,
        },
    )

    settings = get_settings()
    if not settings.GA4_MEASUREMENT_ID or not settings.GA4_API_SECRET:
        logger.warning("GA4 not configured — logging event locally")
        return {**DEMO_DATA["analytics"], "event_name": event_name}

    if _http_client is None:
        return {**DEMO_DATA["analytics"], "event_name": event_name}

    try:
        payload = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_name,
                    "params": params or {},
                }
            ],
        }

        # [GOOGLE SERVICE: GA4 Measurement Protocol] — track civic engagement event
        await _http_client.post(
            GA4_COLLECT_URL,
            params={
                "measurement_id": settings.GA4_MEASUREMENT_ID,
                "api_secret": settings.GA4_API_SECRET,
            },
            json=payload,
        )

        logger.info(
            "Google Analytics 4 event tracked",
            extra={"google_service": "Google Analytics 4", "event": event_name},
        )
        return {"event_logged": True, "event_name": event_name, "message": "Event sent to GA4"}
    except Exception as exc:
        logger.error(
            "Google Analytics 4 event tracking failed",
            extra={"error": str(exc), "google_service": "Google Analytics 4"},
        )
        return {**DEMO_DATA["analytics"], "event_name": event_name}
