"""
routers/checklist.py — Document Checklist Routes
===================================================
Google Service: Google Gemini Vision API
Purpose:        Voter document validation and checklist management

Challenge: "steps in an interactive and easy-to-follow way" —
document preparation is a critical election step.

GOOGLE API CALLS VIA THIS ROUTER:
  - POST /checklist/validate-doc → Gemini Vision (document validation)
"""

import logging
from typing import Any

from fastapi import APIRouter, Request

from limiting import limiter
from models import DocumentValidationRequest, DocumentValidationResponse
from services.gemini_service import validate_document

logger = logging.getLogger("civicpath.routers.checklist")

router = APIRouter(prefix="/checklist", tags=["Checklist"])


@router.post("/validate-doc", response_model=DocumentValidationResponse)
@limiter.limit("10/minute")
async def validate_doc(request: Request, body: DocumentValidationRequest) -> dict[str, Any]:
    """Validate a voter document image using Google Gemini Vision API.

    Google Service: Google Gemini Vision API

    Args:
        request: FastAPI request.
        body: Document image in base64 with document type.

    Returns:
        Validation result with feedback and suggestions.
    """
    logger.info("Validating document", extra={"google_service": "Gemini Vision"})

    # [GOOGLE SERVICE: Gemini Vision] — validate voter document
    result = await validate_document(body.image_base64, body.document_type)

    return {
        "is_valid": result.get("is_valid", True),
        "feedback": result.get("feedback", "Document received"),
        "suggestions": result.get("suggestions", []),
        "google_service": "Google Gemini Vision API",
    }
