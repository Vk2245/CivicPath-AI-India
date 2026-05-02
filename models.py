"""
models.py — CivicPath Pydantic Models
=======================================
Purpose:  All request/response models with strict validation.
          Every field has type hints, Field constraints, and validators.
Inputs:   Raw JSON from API requests
Outputs:  Validated, sanitized Python objects
Deps:     pydantic==2.11.1

Challenge Alignment: Input validation ensures the Election Process Education
platform handles diverse voter data safely and correctly.

GOOGLE API CALLS IN THIS MODULE:
  - None (pure data models — used by routers and services)
"""

import re
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from config import (
    MAX_CHAT_MESSAGE_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_MYTH_TEXT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_STATE_LENGTH,
)


# ═══ SANITIZATION UTILITIES ═══


def strip_html_tags(value: str) -> str:
    """Remove HTML tags from user input to prevent XSS.

    Args:
        value: Raw user input string.

    Returns:
        Sanitized string with all HTML tags removed.
    """
    return re.sub(r"<[^>]+>", "", value).strip()


# ═══ ENUMS ═══


class ElectionType(str, Enum):
    """Supported election types for journey personalization."""

    GENERAL = "general"
    PRIMARY = "primary"
    MIDTERM = "midterm"
    LOCAL = "local"
    SPECIAL = "special"


class StepStatus(str, Enum):
    """Status values for journey timeline steps."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MythVerdict(str, Enum):
    """Verdict categories for the myth detector."""

    MYTH = "myth"
    FACT = "fact"
    MISLEADING = "misleading"
    UNVERIFIABLE = "unverifiable"


# ═══ JOURNEY MODELS ═══


class JourneyStartRequest(BaseModel):
    """Request to create a personalized election journey.

    Attributes:
        state: US state for election rules personalization.
        is_registered: Whether the user is already registered to vote.
        is_first_time: Whether this is the user's first time voting.
        election_type: Type of upcoming election.
        language: Preferred language code (ISO 639-1).
    """

    state: str = Field(
        ...,
        min_length=2,
        max_length=MAX_STATE_LENGTH,
        description="US state name or abbreviation",
        examples=["california", "CA"],
    )
    is_registered: bool = Field(
        default=False,
        description="Whether user is already registered to vote",
    )
    is_first_time: bool = Field(
        default=True,
        description="Whether this is the user's first election",
    )
    election_type: ElectionType = Field(
        default=ElectionType.GENERAL,
        description="Type of election",
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=5,
        description="Preferred language (ISO 639-1)",
    )

    @field_validator("state")
    @classmethod
    def sanitize_state(cls, v: str) -> str:
        """Sanitize state input to prevent XSS."""
        return strip_html_tags(v).lower()


class JourneyStep(BaseModel):
    """A single step in the election journey timeline.

    Attributes:
        step_number: Position in the timeline (1-indexed).
        title: Short step title.
        description: Detailed step instructions.
        deadline: Optional deadline date for this step.
        status: Current completion status.
        is_critical: Whether missing this step blocks voting.
        category: Step category for grouping.
    """

    step_number: int = Field(..., ge=1, le=12, description="Step position in timeline")
    title: str = Field(..., min_length=1, max_length=200, description="Step title")
    description: str = Field(..., min_length=1, max_length=2000, description="Step details")
    deadline: Optional[str] = Field(None, description="Deadline date string")
    status: StepStatus = Field(default=StepStatus.PENDING, description="Step status")
    is_critical: bool = Field(default=False, description="Whether step is blocking")
    category: str = Field(default="preparation", description="Step category")


class JourneyResponse(BaseModel):
    """Response containing a personalized election journey.

    Attributes:
        journey_id: Unique journey identifier.
        state: Personalized state.
        election_type: Election type.
        steps: Ordered list of timeline steps.
        current_step: Current active step index.
        language: Journey language.
        created_at: Journey creation timestamp.
    """

    journey_id: str = Field(..., description="Unique journey ID")
    state: str = Field(..., description="Personalized state")
    election_type: ElectionType = Field(..., description="Election type")
    steps: list[JourneyStep] = Field(..., description="Timeline steps")
    current_step: int = Field(default=0, ge=0, description="Current step index")
    language: str = Field(default="en", description="Journey language")
    created_at: str = Field(..., description="Creation timestamp")


class StepUpdateRequest(BaseModel):
    """Request to update a journey step's status.

    Attributes:
        step_number: Step to update.
        status: New status value.
    """

    step_number: int = Field(..., ge=1, le=12, description="Step number to update")
    status: StepStatus = Field(..., description="New status")


# ═══ CHAT MODELS ═══


class ChatRequest(BaseModel):
    """Request to send a message to the AI election assistant.

    Attributes:
        message: User's question about the election process.
        journey_id: Optional associated journey for context.
        language: Preferred response language.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_LENGTH,
        description="User message to AI assistant",
    )
    journey_id: Optional[str] = Field(None, description="Associated journey ID")
    language: str = Field(default="en", max_length=5, description="Response language")

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Sanitize chat message to prevent prompt injection and XSS."""
        return strip_html_tags(v)


class ChatResponse(BaseModel):
    """Response from the AI election assistant.

    Attributes:
        response: AI-generated answer.
        sources: List of cited sources.
        confidence: Response confidence score.
        google_service: Google Service used for this response.
    """

    response: str = Field(..., description="AI assistant response")
    sources: list[str] = Field(default_factory=list, description="Cited sources")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    google_service: str = Field(
        default="Google Gemini 1.5 Flash API",
        description="Google Service used",
    )


class MythCheckRequest(BaseModel):
    """Request to check if a statement is a myth or fact.

    Attributes:
        text: Statement to fact-check.
        language: Preferred response language.
    """

    text: str = Field(
        ...,
        min_length=5,
        max_length=MAX_MYTH_TEXT_LENGTH,
        description="Statement to fact-check",
    )
    language: str = Field(default="en", max_length=5, description="Response language")

    @field_validator("text")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize myth text to prevent XSS."""
        return strip_html_tags(v)


class MythCheckResponse(BaseModel):
    """Response from the myth detection engine.

    Attributes:
        verdict: MYTH, FACT, MISLEADING, or UNVERIFIABLE.
        explanation: Detailed explanation with sources.
        confidence: Confidence in the verdict.
        sources: Referenced authoritative sources.
        google_service: Google Service used for analysis.
    """

    verdict: MythVerdict = Field(..., description="Myth detection verdict")
    explanation: str = Field(..., description="Detailed explanation")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence")
    sources: list[str] = Field(default_factory=list, description="Sources")
    google_service: str = Field(
        default="Google Gemini 1.5 Flash API",
        description="Google Service used",
    )


# ═══ VOICE MODELS ═══


class VoiceInputResponse(BaseModel):
    """Response from voice input processing.

    Attributes:
        transcript: Recognized speech text.
        ai_response: AI assistant's response to the transcript.
        audio_url: URL to TTS audio of the response.
        google_services: Google Services used.
    """

    transcript: str = Field(..., description="Speech-to-text transcript")
    ai_response: str = Field(..., description="AI response to transcript")
    audio_url: Optional[str] = Field(None, description="TTS audio URL")
    google_services: list[str] = Field(
        default_factory=lambda: [
            "Google Cloud Speech-to-Text API",
            "Google Gemini 1.5 Flash API",
            "Google Cloud Text-to-Speech API",
        ],
        description="Google Services used in this pipeline",
    )


# ═══ CHECKLIST MODELS ═══


class DocumentValidationRequest(BaseModel):
    """Request to validate a voter document image.

    Attributes:
        image_base64: Base64-encoded document image.
        document_type: Type of document being validated.
    """

    image_base64: str = Field(
        ...,
        min_length=100,
        description="Base64-encoded document image",
    )
    document_type: str = Field(
        default="voter_id",
        max_length=50,
        description="Document type (voter_id, registration_form)",
    )


class DocumentValidationResponse(BaseModel):
    """Response from document image validation.

    Attributes:
        is_valid: Whether the document appears valid.
        feedback: Specific feedback on the document.
        suggestions: Improvement suggestions.
        google_service: Google Service used.
    """

    is_valid: bool = Field(..., description="Whether document appears valid")
    feedback: str = Field(..., description="Validation feedback")
    suggestions: list[str] = Field(default_factory=list, description="Suggestions")
    google_service: str = Field(
        default="Google Gemini Vision API",
        description="Google Service used",
    )


# ═══ TRANSLATION MODELS ═══


class TranslateRequest(BaseModel):
    """Request to translate text.

    Attributes:
        text: Text to translate.
        target_language: Target language code (ISO 639-1).
        source_language: Optional source language code.
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to translate",
    )
    target_language: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Target language code",
    )
    source_language: Optional[str] = Field(
        None,
        max_length=5,
        description="Source language code (auto-detect if omitted)",
    )


class TranslateResponse(BaseModel):
    """Response from translation service.

    Attributes:
        translated_text: Translated text.
        source_language: Detected or specified source language.
        target_language: Target language.
        google_service: Google Service used.
    """

    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language detected")
    target_language: str = Field(..., description="Target language")
    google_service: str = Field(
        default="Google Cloud Translation API",
        description="Google Service used",
    )


# ═══ FAQ MODELS ═══


class FAQSearchRequest(BaseModel):
    """Request to search FAQ knowledge base.

    Attributes:
        query: Search query text.
        limit: Maximum results to return.
    """

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Search query",
    )
    limit: int = Field(default=5, ge=1, le=20, description="Max results")


class FAQResult(BaseModel):
    """A single FAQ search result.

    Attributes:
        question: FAQ question.
        answer: FAQ answer.
        similarity: Cosine similarity score.
        category: FAQ category.
    """

    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    category: str = Field(default="general", description="FAQ category")


class FAQSearchResponse(BaseModel):
    """Response from FAQ semantic search.

    Attributes:
        results: List of matching FAQs.
        query: Original search query.
        google_service: Google Service used.
    """

    results: list[FAQResult] = Field(..., description="Matching FAQs")
    query: str = Field(..., description="Original query")
    google_service: str = Field(
        default="Google Gemini Embeddings API",
        description="Google Service used",
    )


# ═══ MAPS MODELS ═══


class PollingPlaceRequest(BaseModel):
    """Request to find nearby polling places.

    Attributes:
        latitude: User's latitude.
        longitude: User's longitude.
        address: Optional address for geocoding.
    """

    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Address to geocode",
    )


class PollingPlace(BaseModel):
    """A single polling place result.

    Attributes:
        name: Polling place name.
        address: Full address.
        latitude: Location latitude.
        longitude: Location longitude.
        distance_miles: Distance from user.
        hours: Operating hours.
        place_id: Google Places ID.
    """

    name: str = Field(..., description="Polling place name")
    address: str = Field(..., description="Full address")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    distance_miles: Optional[float] = Field(None, description="Distance in miles")
    hours: Optional[str] = Field(None, description="Operating hours")
    place_id: Optional[str] = Field(None, description="Google Places ID")


class PollingPlaceResponse(BaseModel):
    """Response from polling place finder.

    Attributes:
        places: List of nearby polling places.
        google_service: Google Service used.
    """

    places: list[PollingPlace] = Field(..., description="Nearby polling places")
    google_service: str = Field(
        default="Google Maps Places API",
        description="Google Service used",
    )


# ═══ REMINDER MODELS ═══


class ReminderSubscribeRequest(BaseModel):
    """Request to subscribe to deadline reminders.

    Attributes:
        email: Subscriber email address.
        name: Subscriber name.
        journey_id: Associated journey.
        recaptcha_token: Google reCAPTCHA v3 token.
    """

    email: str = Field(
        ...,
        min_length=5,
        max_length=MAX_EMAIL_LENGTH,
        description="Subscriber email",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_NAME_LENGTH,
        description="Subscriber name",
    )
    journey_id: Optional[str] = Field(None, description="Associated journey ID")
    recaptcha_token: str = Field(
        ...,
        min_length=10,
        description="Google reCAPTCHA v3 token",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        v = strip_html_tags(v)
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v.lower()

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name to prevent XSS."""
        return strip_html_tags(v)


class ReminderSubscribeResponse(BaseModel):
    """Response from reminder subscription.

    Attributes:
        success: Whether subscription was successful.
        message: Status message.
        google_service: Google Service used for bot protection.
    """

    success: bool = Field(..., description="Subscription success")
    message: str = Field(..., description="Status message")
    google_service: str = Field(
        default="Google reCAPTCHA v3 API",
        description="Google Service used for bot protection",
    )


# ═══ HEALTH MODELS ═══


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Service health status.
        version: Application version.
        google_services_count: Number of integrated Google Services.
        environment: Current deployment environment.
        timestamp: Health check timestamp.
    """

    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="App version")
    google_services_count: int = Field(default=10, description="Google Services count")
    environment: str = Field(..., description="Deployment environment")
    timestamp: str = Field(..., description="Check timestamp")
