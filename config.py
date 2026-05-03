"""
config.py — CivicPath Configuration
=====================================
Purpose:  Centralized configuration using pydantic-settings.
          All environment variables, constants, and magic numbers live here.
Inputs:   Environment variables from .env file
Outputs:  Settings singleton accessible throughout the application
Deps:     pydantic-settings==2.7.1

Google Services Configuration:
  This module configures API keys and project IDs for all 10 Google Services:
  1. Google Gemini API (GEMINI_API_KEY)
  2. Google Cloud Project (GOOGLE_CLOUD_PROJECT)
  3. Google Maps Places API (GOOGLE_MAPS_API_KEY)
  4. Google reCAPTCHA v3 (RECAPTCHA_SECRET_KEY, RECAPTCHA_SITE_KEY)
  5. Google Analytics 4 (GA4_MEASUREMENT_ID, GA4_API_SECRET)

Challenge Alignment: Provides secure, validated configuration for all
services that power the Election Process Education platform.
"""

from functools import lru_cache
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All Google Service API keys, Firebase credentials, and application
    constants are managed here with validation and type safety.

    Attributes:
        ENVIRONMENT: Current deployment environment.
        FRONTEND_URL: Allowed CORS origin for the PWA frontend.
        GEMINI_API_KEY: API key for Google Gemini services (Services 1-3).
        GOOGLE_CLOUD_PROJECT: GCP project ID for Cloud APIs (Services 4-6).
        GOOGLE_APPLICATION_CREDENTIALS: Path to GCP service account JSON.
        GOOGLE_MAPS_API_KEY: API key for Google Maps Places (Service 7).
        RECAPTCHA_SECRET_KEY: Secret key for Google reCAPTCHA v3 (Service 8).
        RECAPTCHA_SITE_KEY: Site key for Google reCAPTCHA v3 (Service 8).
        GA4_MEASUREMENT_ID: Google Analytics 4 measurement ID (Service 9).
        GA4_API_SECRET: Google Analytics 4 API secret (Service 9).
        FIREBASE_PROJECT_ID: Firebase project ID.
        FIREBASE_CREDENTIALS_PATH: Path to Firebase service account JSON.
        RESEND_API_KEY: Resend email service API key.
    """

    # ═══ APPLICATION ═══
    ENVIRONMENT: str = Field(default="development", description="Deployment environment")
    FRONTEND_URL: str = Field(
        default="https://civicpath-abcd123-uc.a.run.app",
        description="Frontend URL for CORS",
    )
    APP_TITLE: str = Field(default="CivicPath", description="Application title")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")

    # ═══ GOOGLE SERVICES (10 integrations) ═══

    # Google Gemini API (Services 1, 2, 3: Flash + Vision + Embeddings)
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_API_KEY2: str = Field(default="", description="Second Google Gemini API key")

    # Google Cloud Project (Services 4, 5, 6: Speech-to-Text + TTS + Translate)
    GOOGLE_CLOUD_PROJECT: str = Field(default="", description="GCP project ID")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="", description="Path to GCP service account JSON"
    )

    # Google Maps Places API (Service 7: Polling Place Finder)
    GOOGLE_MAPS_API_KEY: str = Field(default="", description="Google Maps API key")

    # Google reCAPTCHA v3 (Service 8: Bot Protection)
    RECAPTCHA_SECRET_KEY: str = Field(default="", description="reCAPTCHA secret key")
    RECAPTCHA_SITE_KEY: str = Field(default="", description="reCAPTCHA site key")

    # Google Analytics 4 — Measurement Protocol (Service 9)
    GA4_MEASUREMENT_ID: str = Field(default="", description="GA4 measurement ID")
    GA4_API_SECRET: str = Field(default="", description="GA4 API secret")

    # ═══ FIREBASE ═══
    FIREBASE_PROJECT_ID: str = Field(default="", description="Firebase project ID")
    FIREBASE_CREDENTIALS_PATH: str = Field(default="", description="Path to Firebase credentials")

    # ═══ EMAIL ═══
    RESEND_API_KEY: str = Field(default="", description="Resend email API key")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton.

    Returns:
        Settings: Validated application configuration.
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache so the next call re-reads .env.

    Useful during server startup to guarantee fresh credentials.
    """
    get_settings.cache_clear()


# ═══ APPLICATION CONSTANTS (zero magic numbers) ═══

# Rate limiting constants
RATE_LIMIT_JOURNEY_START: Final[str] = "10/minute"
RATE_LIMIT_CHAT: Final[str] = "20/minute"
RATE_LIMIT_REMINDERS: Final[str] = "5/minute"
RATE_LIMIT_TRANSLATE: Final[str] = "30/minute"
RATE_LIMIT_FAQ: Final[str] = "30/minute"
RATE_LIMIT_MAPS: Final[str] = "15/minute"
RATE_LIMIT_VOICE: Final[str] = "10/minute"

# Cache TTL constants (seconds)
CACHE_TTL_GEMINI: Final[int] = 300
CACHE_TTL_TRANSLATE: Final[int] = 3600
CACHE_TTL_MAPS: Final[int] = 600
CACHE_TTL_STATE_DATA: Final[int] = 86400
CACHE_TTL_FAQ: Final[int] = 1800

# Static assets cache
STATIC_CACHE_MAX_AGE: Final[int] = 86400

# Journey constants
MAX_JOURNEY_STEPS: Final[int] = 12
MIN_JOURNEY_STEPS: Final[int] = 7
DEFAULT_STATE: Final[str] = "bihar"
DEFAULT_ELECTION_TYPE: Final[str] = "general"
DEFAULT_LANGUAGE: Final[str] = "en"

# Input validation limits
MAX_CHAT_MESSAGE_LENGTH: Final[int] = 2000
MAX_MYTH_TEXT_LENGTH: Final[int] = 1000
MAX_STATE_LENGTH: Final[int] = 50
MAX_NAME_LENGTH: Final[int] = 100
MAX_EMAIL_LENGTH: Final[int] = 254
MIN_RECAPTCHA_SCORE: Final[float] = 0.5

# Gemini model configuration
GEMINI_MODEL_NAME: Final[str] = "gemini-1.5-flash"
GEMINI_EMBEDDING_MODEL: Final[str] = "models/embedding-001"
GEMINI_MAX_OUTPUT_TOKENS: Final[int] = 1024
GEMINI_TEMPERATURE: Final[float] = 0.7
GEMINI_MYTH_TEMPERATURE: Final[float] = 0.2

# Supported languages for Google Cloud Translation
SUPPORTED_LANGUAGES: Final[list[str]] = [
    "en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "or", "ur",
]

# reCAPTCHA
RECAPTCHA_VERIFY_URL: Final[str] = "https://www.google.com/recaptcha/api/siteverify"

# GA4 Measurement Protocol
GA4_COLLECT_URL: Final[str] = "https://www.google-analytics.com/mp/collect"

# Maps
MAPS_SEARCH_RADIUS_METERS: Final[int] = 8000
MAPS_MAX_RESULTS: Final[int] = 10
