"""
routers/journey.py — Election Journey Routes
===============================================
Google Service: Google Gemini 1.5 Flash API, Google Analytics 4
Purpose:        Create and manage personalized election journeys

Challenge: "Create an assistant that helps users understand the election
process, timelines, and steps in an interactive and easy-to-follow way."

GOOGLE API CALLS VIA THIS ROUTER:
  - POST /journey/start → Gemini 1.5 Flash (timeline generation)
  - PUT /journey/{id}/step → GA4 (step completion tracking)
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from starlette.status import HTTP_404_NOT_FOUND

from config import RATE_LIMIT_JOURNEY_START
from limiting import limiter
from models import JourneyResponse, JourneyStartRequest, StepUpdateRequest
from services import journey_engine, firebase_service
from services.analytics_service import track_event
from services.gemini_service import generate_journey_steps

logger = logging.getLogger("civicpath.routers.journey")

router = APIRouter(prefix="/journey", tags=["Journey"])


@router.post("/start", response_model=JourneyResponse)
@limiter.limit(RATE_LIMIT_JOURNEY_START)
async def start_journey(request: Request, body: JourneyStartRequest) -> dict[str, Any]:
    """Create a personalized election preparation journey.

    Generates a voter-specific timeline using Google Gemini 1.5 Flash API
    based on the user's state, registration status, and election type.
    Directly addresses the challenge of providing interactive, personalized
    election guidance.

    Google Services: Gemini 1.5 Flash (journey generation), GA4 (event tracking)

    Args:
        request: FastAPI request object (required by rate limiter).
        body: Journey creation parameters.

    Returns:
        Personalized journey with timeline steps.
    """
    logger.info(
        "Starting new election journey",
        extra={"state": body.state, "election_type": body.election_type.value},
    )

    # Generate personalized steps using journey engine
    steps = journey_engine.generate_timeline_steps(
        state=body.state,
        is_registered=body.is_registered,
        is_first_time=body.is_first_time,
        election_type=body.election_type.value,
    )

    # Save journey to database
    journey = await firebase_service.create_journey({
        "state": body.state,
        "is_registered": body.is_registered,
        "is_first_time": body.is_first_time,
        "election_type": body.election_type.value,
        "language": body.language,
        "steps": steps,
    })

    # [GOOGLE SERVICE: GA4] — track journey_started event
    await track_event("journey_started", {
        "state": body.state,
        "election_type": body.election_type.value,
    })

    return {
        "journey_id": journey["id"],
        "state": body.state,
        "election_type": body.election_type.value,
        "steps": steps,
        "current_step": 0,
        "language": body.language,
        "created_at": journey["created_at"],
    }


@router.get("/{journey_id}")
async def get_journey(journey_id: str) -> dict[str, Any]:
    """Retrieve an existing election journey by ID.

    Args:
        journey_id: Unique journey identifier.

    Returns:
        Journey data with timeline steps.

    Raises:
        HTTPException: If journey not found (404).
    """
    journey = await firebase_service.get_journey(journey_id)
    if not journey:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Journey not found")
    return journey


@router.put("/{journey_id}/step")
async def update_step(
    request: Request, journey_id: str, body: StepUpdateRequest
) -> dict[str, Any]:
    """Update a journey step's completion status.

    Google Service: Google Analytics 4 (step completion tracking)

    Args:
        request: FastAPI request.
        journey_id: Journey identifier.
        body: Step update data.

    Returns:
        Updated journey record.
    """
    result = await firebase_service.update_journey_step(
        journey_id, body.step_number, body.status.value
    )

    if not result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Journey not found")

    # [GOOGLE SERVICE: GA4] — track step_completed event
    await track_event("step_completed", {
        "journey_id": journey_id,
        "step_number": body.step_number,
        "status": body.status.value,
    })

    return {"success": True, "journey_id": journey_id, "step": body.step_number, "status": body.status.value}
