"""
routers/maps.py — Polling Place Finder Routes
================================================
Google Service: Google Maps Places API
Purpose:        Find nearby polling places by location

GOOGLE API CALLS VIA THIS ROUTER:
  - GET /polling-places → Maps Places API (location search)
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Query, Request

from config import RATE_LIMIT_MAPS
from limiting import limiter
from models import PollingPlaceResponse
from services.maps_service import find_polling_places

logger = logging.getLogger("civicpath.routers.maps")

router = APIRouter(tags=["Maps"])


@router.get("/polling-places", response_model=PollingPlaceResponse)
@limiter.limit(RATE_LIMIT_MAPS)
async def get_polling_places(
    request: Request,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    address: Optional[str] = Query(None, max_length=500),
) -> dict[str, Any]:
    """Find nearby polling places using Google Maps Places API.

    Google Service: Google Maps Places API

    Args:
        request: FastAPI request.
        latitude: User latitude.
        longitude: User longitude.
        address: Address to geocode.

    Returns:
        List of nearby polling places.
    """
    logger.info("Finding polling places", extra={"google_service": "Maps Places API"})

    # [GOOGLE SERVICE: Maps Places API] — find polling locations
    places = await find_polling_places(latitude, longitude, address)

    return {
        "places": places,
        "google_service": "Google Maps Places API",
    }
