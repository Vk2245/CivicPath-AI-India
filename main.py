"""
main.py — CivicPath Application Entry Point
============================================
Purpose:  FastAPI application for CivicPath — an AI-powered election
          process education platform addressing the challenge:
          "Create an assistant that helps users understand the election
          process, timelines, and steps in an interactive and
          easy-to-follow way."
Inputs:   HTTP requests from PWA frontend
Outputs:  JSON API responses, static PWA files
Deps:     fastapi, uvicorn, firebase, google-generativeai,
          google-cloud-speech, google-cloud-texttospeech,
          google-cloud-translate, googlemaps, slowapi

GOOGLE SERVICES INTEGRATED (10 distinct services):
───────────────────────────────────────────────────
1.  Google Gemini 1.5 Flash API      → services/gemini_service.py
2.  Google Gemini Vision API         → services/gemini_service.py
3.  Google Gemini Embeddings API     → services/gemini_service.py
4.  Google Cloud Speech-to-Text API  → services/speech_service.py
5.  Google Cloud Text-to-Speech API  → services/speech_service.py
6.  Google Cloud Translation API     → services/translate_service.py
7.  Google Maps Places API           → services/maps_service.py
8.  Google reCAPTCHA v3 API          → services/recaptcha_service.py
9.  Google Analytics 4 API           → services/analytics_service.py
10. Google Fonts API                 → static/index.html

ARCHITECTURE:
  Client (PWA) → FastAPI (Cloud Run) → Firebase (PostgreSQL + Auth + pgvector)
                                 → Google AI APIs (Gemini, Speech, Translate)
                                 → Google Maps Places API
                                 → Google reCAPTCHA v3

DEPLOYMENT:
  Backend:  Cloud Run Web Service (https://civicpath-abcd123-uc.a.run.app)
  Database: Firebase (PostgreSQL + Realtime + Auth + Storage)
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import STATIC_CACHE_MAX_AGE, get_settings
from exceptions import CivicPathError
from limiting import limiter
from routers import chat, checklist, faq, health, journey, maps, reminders, translate
from security import SecurityHeadersMiddleware
from services.analytics_service import init_analytics_client
from services.gemini_service import init_gemini_client
from services.maps_service import init_maps_client
from services.recaptcha_service import init_recaptcha_client
from services.speech_service import init_speech_clients
from services.firebase_service import init_firebase_client
from services.translate_service import init_translate_client
from services.reminder_service import init_reminder_client

# ═══ LOGGING CONFIGURATION ═══
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("civicpath.main")


# ═══ APPLICATION LIFESPAN ═══
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler — initialize and cleanup services.

    Initializes all 10 Google Services and database connections during
    startup. Cleans up resources during shutdown.

    Google Services initialized:
      1. Google Gemini 1.5 Flash + Vision + Embeddings
      2. Google Cloud Speech-to-Text + Text-to-Speech
      3. Google Cloud Translation API
      4. Google Maps Places API
      5. Google reCAPTCHA v3
      6. Google Analytics 4
    """
    logger.info("CivicPath starting — initializing 10 Google Services...")

    # Shared HTTP client for REST-based Google services
    http_client = httpx.AsyncClient(timeout=30.0)

    # Initialize all Google Services
    await init_gemini_client()        # Services 1, 2, 3
    await init_speech_clients()       # Services 4, 5
    await init_translate_client()     # Service 6
    await init_maps_client()          # Service 7
    await init_recaptcha_client(http_client)  # Service 8
    await init_analytics_client(http_client)  # Service 9
    # Service 10 (Google Fonts) loaded via CDN in static/index.html

    # Initialize database
    await init_firebase_client()
    await init_reminder_client(http_client)

    logger.info("CivicPath initialized — all 10 Google Services ready")
    yield

    # Cleanup
    await http_client.aclose()
    logger.info("CivicPath shutdown complete")


# ═══ APPLICATION INSTANCE ═══
settings = get_settings()

app = FastAPI(
    title="CivicPath — Personalized Election Journey Guide",
    description=(
        "AI-powered election process education platform integrating "
        "10 Google Services. Challenge: 'Create an assistant that helps "
        "users understand the election process, timelines, and steps "
        "in an interactive and easy-to-follow way.'"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ═══ MIDDLEWARE ═══

# Security headers (7 headers on every response)
app.add_middleware(SecurityHeadersMiddleware)

# CORS — restricted to explicit origins (never wildcard *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ═══ EXCEPTION HANDLERS ═══
@app.exception_handler(CivicPathError)
async def civicpath_error_handler(request: Request, exc: CivicPathError) -> JSONResponse:
    """Handle all CivicPath application errors.

    Args:
        request: The incoming request.
        exc: The CivicPath error that was raised.

    Returns:
        JSON error response with appropriate status code.
    """
    logger.error(f"CivicPath error: {exc.message}", extra={"detail": exc.detail})
    return JSONResponse(
        status_code=400,
        content={"error": exc.message, "detail": exc.detail},
    )


# ═══ ROUTERS ═══
app.include_router(health.router)
app.include_router(journey.router)
app.include_router(chat.router)
app.include_router(checklist.router)
app.include_router(reminders.router)
app.include_router(translate.router)
app.include_router(faq.router)
app.include_router(maps.router)

# ═══ STATIC FILES ═══
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# ═══ ENTRY POINT ═══
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.ENVIRONMENT == "development",
    )
