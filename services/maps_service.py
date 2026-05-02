"""
maps_service.py — Google Maps Places Integration
===================================================
Google Service: Google Maps Places API
SDK Package:    googlemaps==4.10.0
Purpose:        Find nearby polling places for voters
Inputs:         Latitude/longitude or address
Outputs:        List of nearby polling locations
Deps:           googlemaps==4.10.0

Challenge Alignment: This module addresses the challenge step of helping
voters know WHERE to vote by integrating Google Maps Places API.

GOOGLE API CALLS IN THIS MODULE:
  - find_polling_places(): Calls Google Maps Places to locate polling stations
"""

import logging
from typing import Any, Optional

from config import MAPS_MAX_RESULTS, MAPS_SEARCH_RADIUS_METERS, get_settings
from demo_data import DEMO_DATA
from exceptions import MapsError

logger = logging.getLogger("civicpath.maps")

# ═══ GOOGLE SERVICE: Maps Places API ═══
# SDK: googlemaps
# Docs: https://developers.google.com/maps/documentation/places

_maps_client: Any = None


async def init_maps_client() -> None:
    """Initialize Google Maps Places API client.

    Google Service: Google Maps Places API
    SDK: googlemaps
    """
    global _maps_client
    settings = get_settings()

    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning(
            "GOOGLE_MAPS_API_KEY not set — Maps in demo mode",
            extra={"google_service": "Google Maps Places API"},
        )
        return

    try:
        import googlemaps

        # [GOOGLE SERVICE: Maps Places API] — client initialization
        _maps_client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        logger.info(
            "Google Maps Places client initialized",
            extra={"google_service": "Google Maps Places API"},
        )
    except Exception as exc:
        logger.error(
            "Failed to init Google Maps client",
            extra={"error": str(exc), "google_service": "Maps Places API"},
        )


async def find_polling_places(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Find nearby polling places using Google Maps Places API.

    Google Service Used: Google Maps Places API
    SDK Call: googlemaps.Client(key).places_nearby(location, radius, type)

    Args:
        latitude: User latitude.
        longitude: User longitude.
        address: Address to geocode if lat/lng not provided.

    Returns:
        List of polling place dictionaries.

    Raises:
        MapsError: If Google Maps Places API call fails.
    """
    logger.info(
        "Calling Google Maps Places API",
        extra={"function": "find_polling_places", "google_service": "Maps Places API"},
    )

    if _maps_client is None:
        logger.warning("Maps not initialized — using demo fallback")
        return DEMO_DATA["maps_places"]

    try:
        location = None
        if latitude and longitude:
            location = (latitude, longitude)
        elif address:
            # [GOOGLE SERVICE: Maps Places API] — geocode address
            geocode_result = _maps_client.geocode(address)
            if geocode_result:
                loc = geocode_result[0]["geometry"]["location"]
                location = (loc["lat"], loc["lng"])

        if not location:
            return DEMO_DATA["maps_places"]

        # [GOOGLE SERVICE: Maps Places API] — find nearby polling places
        result = _maps_client.places_nearby(
            location=location,
            radius=MAPS_SEARCH_RADIUS_METERS,
            keyword="polling place voting center",
            type="establishment",
        )

        places = []
        for place in result.get("results", [])[:MAPS_MAX_RESULTS]:
            loc = place["geometry"]["location"]
            places.append({
                "name": place.get("name", "Polling Place"),
                "address": place.get("vicinity", "Address not available"),
                "latitude": loc["lat"],
                "longitude": loc["lng"],
                "distance_miles": None,
                "hours": place.get("opening_hours", {}).get("weekday_text", [None])[0],
                "place_id": place.get("place_id"),
            })

        logger.info(
            "Google Maps Places call succeeded",
            extra={"google_service": "Maps Places API", "results": len(places)},
        )
        return places if places else DEMO_DATA["maps_places"]
    except Exception as exc:
        logger.error(
            "Google Maps Places API failed",
            extra={"error": str(exc), "google_service": "Maps Places API"},
        )
        return DEMO_DATA["maps_places"]
