"""
exceptions.py — CivicPath Exception Hierarchy
===============================================
Purpose:  Centralized, typed exception hierarchy for the entire application.
          Every service and router raises specific exceptions, never bare
          Exception or generic HTTPException.
Inputs:   None (exception class definitions only)
Outputs:  Exception classes importable by all modules
Deps:     None (stdlib only)

Challenge Alignment: Structured error handling supports the Election Process
Education platform's reliability — users never see cryptic errors during
their voter preparation journey.
"""

from typing import Any


class CivicPathError(Exception):
    """Base exception for all CivicPath application errors.

    All custom exceptions inherit from this class, enabling
    catch-all handlers while preserving specific error types.

    Attributes:
        message: Human-readable error description.
        detail: Additional context for logging/debugging.
    """

    def __init__(self, message: str = "An error occurred", detail: Any = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class JourneyError(CivicPathError):
    """Raised when journey creation or navigation fails.

    Examples: invalid state code, journey not found, step out of range.
    """

    pass


class GeminiServiceError(CivicPathError):
    """Raised when Google Gemini API calls fail.

    Covers: Gemini 1.5 Flash (chat/myth), Vision (document),
    and Embeddings (semantic search) API failures.

    Google Services: Gemini 1.5 Flash, Gemini Vision, Gemini Embeddings
    """

    pass


class SpeechServiceError(CivicPathError):
    """Raised when Google Cloud Speech-to-Text or Text-to-Speech fails.

    Google Services: Cloud Speech-to-Text, Cloud Text-to-Speech
    """

    pass


class TranslationError(CivicPathError):
    """Raised when Google Cloud Translation API fails.

    Google Service: Cloud Translation API
    """

    pass


class MapsError(CivicPathError):
    """Raised when Google Maps Places API fails.

    Google Service: Google Maps Places API
    """

    pass


class RecaptchaError(CivicPathError):
    """Raised when Google reCAPTCHA v3 verification fails.

    Google Service: Google reCAPTCHA v3 API
    """

    pass


class AnalyticsError(CivicPathError):
    """Raised when Google Analytics 4 event tracking fails.

    Google Service: Google Analytics 4 (Measurement Protocol)
    """

    pass


class AuthError(CivicPathError):
    """Raised when authentication or authorization fails.

    Covers: Firebase Auth, anonymous session, token validation.
    """

    pass


class ValidationError(CivicPathError):
    """Raised when input validation fails beyond Pydantic constraints.

    Covers: business logic validation, cross-field validation,
    sanitization failures.
    """

    pass


class FirebaseError(CivicPathError):
    """Raised when Firebase database operations fail.

    Covers: CRUD operations, RLS policy violations, connection errors.
    """

    pass


class ReminderError(CivicPathError):
    """Raised when reminder subscription or email delivery fails.

    Covers: email validation, Resend API failures, duplicate subscriptions.
    """

    pass
