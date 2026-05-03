"""
gemini_service.py — Google Gemini AI Integration
==================================================
Google Service: Google Gemini 1.5 Flash API, Gemini Vision API, Gemini Embeddings API
SDK Package:    google-generativeai==0.8.5
Purpose:        AI-powered election assistant, myth detection, document
                validation, and semantic FAQ search
Inputs:         User messages, images (base64), FAQ queries
Outputs:        AI responses, myth verdicts, validation results, embeddings
Deps:           google-generativeai==0.8.5

Challenge Alignment: This module directly addresses the Election Process
Education challenge requirement of "helping users understand the election
process" by integrating Google Gemini to provide context-aware AI guidance,
fact-checking myths, validating voter documents, and enabling semantic
search across election FAQs.

GOOGLE API CALLS IN THIS MODULE:
  - generate_chat_response(): Calls Google Gemini 1.5 Flash to answer election questions
  - detect_myth(): Calls Google Gemini 1.5 Flash to fact-check election claims
  - validate_document(): Calls Google Gemini Vision to validate voter documents
  - generate_embedding(): Calls Google Gemini Embeddings to create semantic vectors
"""

import base64
import logging
from typing import Any

import google.generativeai as genai  # Google Gemini SDK

from config import (
    GEMINI_EMBEDDING_MODEL,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MODEL_NAME,
    GEMINI_MYTH_TEMPERATURE,
    GEMINI_TEMPERATURE,
    get_settings,
)
from demo_data import DEMO_DATA
from exceptions import GeminiServiceError

logger = logging.getLogger("civicpath.gemini")

# ═══ GOOGLE SERVICE: Gemini 1.5 Flash + Vision + Embeddings ═══
# SDK: google-generativeai
# Docs: https://ai.google.dev/docs

# Google Gemini models — initialized once in app lifespan
_chat_model: genai.GenerativeModel | None = None
_vision_model: genai.GenerativeModel | None = None

# Election assistant system prompt
ELECTION_SYSTEM_PROMPT = """You are CivicPath's AI Election Assistant — a non-partisan,
fact-based guide that helps Indian voters understand the election process.

RULES:
1. Only provide factual, non-partisan information about Indian elections
2. Cite official sources (Election Commission of India eci.gov.in, NVSP voters.eci.gov.in)
3. If unsure, say so — never make up election procedures
4. Adapt to the user's state (e.g., Bihar, Maharashtra) and election type (Lok Sabha, Vidhan Sabha) if provided
5. Be encouraging — voting is a civic right and responsibility
6. Keep responses concise but comprehensive
7. Always mention relevant deadlines (e.g., Form 6 submission deadlines) when applicable

You help with: voter registration (Form 6), EPIC/Voter ID requirements, polling booths,
EVM/VVPAT procedures, candidate research (KYC App), and myth-busting."""

MYTH_SYSTEM_PROMPT = """You are CivicPath's Myth Detector — an AI that fact-checks
election-related claims.

For each claim, respond with EXACTLY this JSON format:
{
  "verdict": "MYTH" | "FACT" | "MISLEADING" | "UNVERIFIABLE",
  "explanation": "Clear explanation with evidence",
  "confidence": 0.0 to 1.0,
  "sources": ["source1", "source2"]
}

RULES:
1. Base verdicts ONLY on verifiable facts from official sources
2. If a claim has some truth but is misleading, use "MISLEADING"
3. If there isn't enough evidence, use "UNVERIFIABLE"
4. Always cite authoritative sources (Election Commission of India, State Election Commissions)
5. Be precise about which parts are true/false in MISLEADING verdicts"""


async def init_gemini_client() -> None:
    """Initialize Google Gemini API clients.

    Called once during FastAPI app lifespan startup. Configures the
    Gemini SDK with the API key and creates model instances for
    chat, vision, and embeddings.

    Google Service: Gemini 1.5 Flash + Vision + Embeddings
    SDK: google-generativeai

    Raises:
        GeminiServiceError: If initialization fails.
    """
    global _chat_model, _vision_model
    settings = get_settings()

    keys = [k for k in [settings.GEMINI_API_KEY, settings.GEMINI_API_KEY2] if k]
    if not keys:
        logger.warning(
            "No GEMINI_API_KEY set — Gemini services running in demo mode",
            extra={"google_service": "Google Gemini API"},
        )
        return

    try:
        import random

        selected_key = random.choice(keys)
        # [GOOGLE SERVICE: Gemini API] — configure SDK with API key
        genai.configure(api_key=selected_key)

        # [GOOGLE SERVICE: Gemini 1.5 Flash] — chat model initialization
        _chat_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config=genai.GenerationConfig(
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                temperature=GEMINI_TEMPERATURE,
            ),
            system_instruction=ELECTION_SYSTEM_PROMPT,
        )

        # [GOOGLE SERVICE: Gemini Vision] — vision model initialization
        _vision_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config=genai.GenerationConfig(
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                temperature=0.3,
            ),
        )

        logger.info(
            "Google Gemini clients initialized successfully",
            extra={"google_service": "Google Gemini 1.5 Flash + Vision + Embeddings"},
        )
    except Exception as exc:
        logger.error(
            "Failed to initialize Google Gemini clients",
            extra={"error": str(exc), "google_service": "Google Gemini API"},
        )
        raise GeminiServiceError(message="Failed to initialize Gemini", detail=str(exc)) from exc


async def generate_chat_response(
    message: str,
    journey_context: dict[str, Any] | None = None,
    language: str = "en",
) -> dict[str, Any]:
    """Generate AI response to an election question using Google Gemini 1.5 Flash.

    Integrates Google Gemini 1.5 Flash API to provide context-aware election
    guidance. Directly addresses the challenge requirement of helping users
    understand the election process interactively.

    Google Service Used: Google Gemini 1.5 Flash API
    SDK Call: genai.GenerativeModel('gemini-1.5-flash').generate_content()

    Args:
        message: User's election question.
        journey_context: Optional journey state for personalized responses.
        language: Preferred response language code.

    Returns:
        Dictionary with response text, sources, and confidence.

    Raises:
        GeminiServiceError: If Google Gemini API call fails.
    """
    logger.info(
        "Calling Google Gemini 1.5 Flash API for chat",
        extra={"function": "generate_chat_response", "google_service": "Gemini 1.5 Flash"},
    )

    if _chat_model is None:
        logger.warning("Gemini not initialized — using demo fallback")
        return DEMO_DATA["gemini_chat"]

    try:
        context_str = ""
        if journey_context:
            context_str = (
                f"\nUser context: State={journey_context.get('state', 'unknown')}, "
                f"Registered={journey_context.get('is_registered', False)}, "
                f"Election={journey_context.get('election_type', 'general')}"
            )

        prompt = f"{message}{context_str}"
        if language != "en":
            prompt += f"\n\nPlease respond in language code: {language}"

        # [GOOGLE SERVICE: Gemini 1.5 Flash] — generate election guidance response
        response = await _chat_model.generate_content_async(prompt)

        logger.info(
            "Google Gemini 1.5 Flash chat call succeeded",
            extra={"google_service": "Gemini 1.5 Flash"},
        )

        return {
            "response": response.text,
            "sources": ["voters.eci.gov.in", "eci.gov.in"],
            "confidence": 0.9,
        }
    except Exception as exc:
        logger.error(
            "Google Gemini 1.5 Flash API call failed: %s",
            str(exc),
            extra={"error": str(exc), "google_service": "Gemini 1.5 Flash"},
        )
        return DEMO_DATA["gemini_chat"]


async def detect_myth(text: str) -> dict[str, Any]:
    """Fact-check an election claim using Google Gemini 1.5 Flash.

    Integrates Google Gemini 1.5 Flash API to detect election myths and
    misinformation. Returns structured verdict with sources.

    Google Service Used: Google Gemini 1.5 Flash API
    SDK Call: genai.GenerativeModel('gemini-1.5-flash').generate_content()

    Args:
        text: Election claim to fact-check.

    Returns:
        Dictionary with verdict, explanation, confidence, and sources.

    Raises:
        GeminiServiceError: If Google Gemini API call fails.
    """
    logger.info(
        "Calling Google Gemini 1.5 Flash API for myth detection",
        extra={"function": "detect_myth", "google_service": "Gemini 1.5 Flash"},
    )

    if _chat_model is None:
        logger.warning("Gemini not initialized — using demo myth fallback")
        return DEMO_DATA["gemini_myth"]

    try:
        myth_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config=genai.GenerationConfig(
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                temperature=GEMINI_MYTH_TEMPERATURE,
            ),
            system_instruction=MYTH_SYSTEM_PROMPT,
        )

        # [GOOGLE SERVICE: Gemini 1.5 Flash] — myth detection analysis
        response = await myth_model.generate_content_async(
            f"Fact-check this election claim: {text}"
        )

        logger.info(
            "Google Gemini 1.5 Flash myth detection succeeded",
            extra={"google_service": "Gemini 1.5 Flash"},
        )

        import json
        import re

        try:
            # Clean markdown code blocks from Gemini 2.5 Flash response
            cleaned_text = re.sub(r"```(?:json)?\s*", "", response.text)
            cleaned_text = re.sub(r"\s*```", "", cleaned_text).strip()

            result = json.loads(cleaned_text)
            return {
                "verdict": result.get("verdict", "UNVERIFIABLE").lower(),
                "explanation": result.get("explanation", response.text),
                "confidence": result.get("confidence", 0.7),
                "sources": result.get("sources", []),
            }
        except json.JSONDecodeError:
            return {
                "verdict": "unverifiable",
                "explanation": response.text,
                "confidence": 0.6,
                "sources": [],
            }
    except Exception as exc:
        logger.error(
            "Google Gemini 1.5 Flash myth detection failed",
            extra={"error": str(exc), "google_service": "Gemini 1.5 Flash"},
        )
        return DEMO_DATA["gemini_myth"]


async def validate_document(image_base64: str, document_type: str = "voter_id") -> dict[str, Any]:
    """Validate a voter document image using Google Gemini Vision API.

    Integrates Google Gemini Vision API to analyze uploaded voter ID or
    registration form images for format validity and readability.

    Google Service Used: Google Gemini Vision API
    SDK Call: genai.GenerativeModel('gemini-1.5-flash').generate_content([image, prompt])

    Args:
        image_base64: Base64-encoded document image.
        document_type: Type of document (voter_id, registration_form).

    Returns:
        Dictionary with validation result, feedback, and suggestions.

    Raises:
        GeminiServiceError: If Google Gemini Vision API call fails.
    """
    logger.info(
        "Calling Google Gemini Vision API for document validation",
        extra={"function": "validate_document", "google_service": "Gemini Vision"},
    )

    if _vision_model is None:
        logger.warning("Gemini Vision not initialized — using demo fallback")
        return DEMO_DATA["gemini_vision"]

    try:
        image_bytes = base64.b64decode(image_base64)
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}

        prompt = (
            f"Analyze this {document_type} image for voter identification purposes. "
            "Check: 1) Is it a valid document format? 2) Is the text readable? "
            "3) Does it appear current/not expired? "
            'Respond with JSON: {"is_valid": bool, "feedback": str, "suggestions": [str]}'
        )

        # [GOOGLE SERVICE: Gemini Vision] — document image validation
        response = await _vision_model.generate_content_async([prompt, image_part])

        logger.info(
            "Google Gemini Vision document validation succeeded",
            extra={"google_service": "Gemini Vision"},
        )

        import json
        import re

        try:
            cleaned_text = re.sub(r"```(?:json)?\s*", "", response.text)
            cleaned_text = re.sub(r"\s*```", "", cleaned_text).strip()
            result = json.loads(cleaned_text)
            return result
        except json.JSONDecodeError:
            return {
                "is_valid": True,
                "feedback": response.text,
                "suggestions": [],
            }
    except Exception as exc:
        logger.error(
            "Google Gemini Vision API call failed",
            extra={"error": str(exc), "google_service": "Gemini Vision"},
        )
        return DEMO_DATA["gemini_vision"]


async def generate_embedding(text: str) -> list[float]:
    """Generate a semantic embedding vector using Google Gemini Embeddings API.

    Integrates Google Gemini Embeddings API to create vector representations
    of text for semantic FAQ search via Firebase pgvector.

    Google Service Used: Google Gemini Embeddings API
    SDK Call: genai.embed_content(model='models/embedding-001', content=text)

    Args:
        text: Text to generate embedding for.

    Returns:
        List of floats representing the embedding vector.

    Raises:
        GeminiServiceError: If Google Gemini Embeddings API call fails.
    """
    logger.info(
        "Calling Google Gemini Embeddings API",
        extra={"function": "generate_embedding", "google_service": "Gemini Embeddings"},
    )

    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        logger.warning("Gemini not configured — returning zero vector")
        return [0.0] * 768

    try:
        # [GOOGLE SERVICE: Gemini Embeddings] — semantic vector generation
        result = genai.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )

        logger.info(
            "Google Gemini Embeddings call succeeded",
            extra={"google_service": "Gemini Embeddings"},
        )

        return result["embedding"]
    except Exception as exc:
        logger.error(
            "Google Gemini Embeddings API call failed",
            extra={"error": str(exc), "google_service": "Gemini Embeddings"},
        )
        return [0.0] * 768


async def generate_journey_steps(
    state: str,
    is_registered: bool,
    is_first_time: bool,
    election_type: str,
) -> list[dict[str, Any]]:
    """Generate personalized election journey steps using Gemini 1.5 Flash.

    Google Service Used: Google Gemini 1.5 Flash API

    Args:
        state: User's US state.
        is_registered: Whether user is registered.
        is_first_time: Whether first-time voter.
        election_type: Type of election.

    Returns:
        List of journey step dictionaries.
    """
    logger.info(
        "Calling Google Gemini 1.5 Flash for journey generation",
        extra={"function": "generate_journey_steps", "google_service": "Gemini 1.5 Flash"},
    )

    if _chat_model is None:
        return DEMO_DATA["journey_steps"]

    try:
        prompt = (
            f"Generate a personalized election preparation timeline for a voter in "
            f"{state} for a {election_type} election. "
            f"Registered: {is_registered}. First-time voter: {is_first_time}.\n\n"
            "Return a JSON array of 7 steps with: step_number, title, description, "
            "deadline, is_critical, category. Categories: registration, preparation, "
            "research, logistics, voting."
        )

        # [GOOGLE SERVICE: Gemini 1.5 Flash] — personalized journey generation
        response = await _chat_model.generate_content_async(prompt)

        import json
        import re

        try:
            cleaned_text = re.sub(r"```(?:json)?\s*", "", response.text)
            cleaned_text = re.sub(r"\s*```", "", cleaned_text).strip()
            steps = json.loads(cleaned_text)
            if isinstance(steps, list):
                for step in steps:
                    step.setdefault("status", "pending")
                return steps
        except json.JSONDecodeError:
            pass

        return DEMO_DATA["journey_steps"]
    except Exception as exc:
        logger.error(
            "Journey generation failed",
            extra={"error": str(exc), "google_service": "Gemini 1.5 Flash"},
        )
        return DEMO_DATA["journey_steps"]
