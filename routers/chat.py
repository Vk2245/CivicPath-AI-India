"""
routers/chat.py — AI Chat & Myth Detection Routes
====================================================
Google Service: Google Gemini 1.5 Flash API, Cloud Speech-to-Text, Cloud Text-to-Speech
Purpose:        AI election assistant, myth detector, voice input

Challenge: "Create an assistant that helps users understand the election
process, timelines, and steps in an interactive and easy-to-follow way."

GOOGLE API CALLS VIA THIS ROUTER:
  - POST /chat → Gemini 1.5 Flash (election Q&A)
  - POST /chat/myth-check → Gemini 1.5 Flash (myth detection)
  - POST /chat/voice-input → Cloud STT + Gemini + Cloud TTS
"""

import logging
from typing import Any

from fastapi import APIRouter, Request, UploadFile, File

from config import RATE_LIMIT_CHAT, RATE_LIMIT_VOICE
from limiting import limiter
from models import ChatRequest, ChatResponse, MythCheckRequest, MythCheckResponse, VoiceInputResponse
from services.gemini_service import detect_myth, generate_chat_response
from services.speech_service import synthesize_speech, transcribe_audio
from services import firebase_service

logger = logging.getLogger("civicpath.routers.chat")

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT_CHAT)
async def chat(request: Request, body: ChatRequest) -> dict[str, Any]:
    """Send a message to the AI election assistant.

    Integrates Google Gemini 1.5 Flash API for context-aware election Q&A.

    Google Service: Google Gemini 1.5 Flash API

    Args:
        request: FastAPI request object.
        body: Chat message with optional journey context.

    Returns:
        AI-generated response with sources and confidence.
    """
    logger.info("Processing chat message", extra={"google_service": "Gemini 1.5 Flash"})

    # Get journey context if provided
    journey_context = None
    if body.journey_id:
        journey = await firebase_service.get_journey(body.journey_id)
        if journey:
            journey_context = journey

    # [GOOGLE SERVICE: Gemini 1.5 Flash] — generate response
    result = await generate_chat_response(
        message=body.message,
        journey_context=journey_context,
        language=body.language,
    )

    # Save chat history
    await firebase_service.save_chat_message(body.journey_id, "user", body.message)
    await firebase_service.save_chat_message(body.journey_id, "assistant", result["response"])

    return {
        "response": result["response"],
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", 0.0),
        "google_service": "Google Gemini 1.5 Flash API",
    }


@router.post("/myth-check", response_model=MythCheckResponse)
@limiter.limit(RATE_LIMIT_CHAT)
async def myth_check(request: Request, body: MythCheckRequest) -> dict[str, Any]:
    """Fact-check an election claim using AI myth detection.

    Google Service: Google Gemini 1.5 Flash API

    Args:
        request: FastAPI request.
        body: Claim to fact-check.

    Returns:
        Myth verdict with explanation and sources.
    """
    logger.info("Processing myth check", extra={"google_service": "Gemini 1.5 Flash"})

    # [GOOGLE SERVICE: Gemini 1.5 Flash] — myth detection
    result = await detect_myth(body.text)

    return {
        "verdict": result["verdict"],
        "explanation": result["explanation"],
        "confidence": result.get("confidence", 0.0),
        "sources": result.get("sources", []),
        "google_service": "Google Gemini 1.5 Flash API",
    }


@router.post("/voice-input", response_model=VoiceInputResponse)
@limiter.limit(RATE_LIMIT_VOICE)
async def voice_input(request: Request, audio: UploadFile = File(...)) -> dict[str, Any]:
    """Process voice input: STT → Gemini → TTS pipeline.

    Full voice pipeline using 3 Google Services:
    1. Cloud Speech-to-Text: transcribe audio
    2. Gemini 1.5 Flash: generate response
    3. Cloud Text-to-Speech: synthesize response audio

    Google Services: Cloud STT, Gemini 1.5 Flash, Cloud TTS

    Args:
        request: FastAPI request.
        audio: Uploaded audio file.

    Returns:
        Transcript, AI response, and TTS audio URL.
    """
    logger.info("Processing voice input pipeline", extra={"google_service": "Cloud STT + Gemini + Cloud TTS"})

    # Step 1: [GOOGLE SERVICE: Cloud Speech-to-Text] — transcribe
    audio_bytes = await audio.read()
    stt_result = await transcribe_audio(audio_bytes)
    transcript = stt_result.get("transcript", "")

    # Step 2: [GOOGLE SERVICE: Gemini 1.5 Flash] — generate response
    chat_result = await generate_chat_response(message=transcript)

    # Step 3: [GOOGLE SERVICE: Cloud Text-to-Speech] — synthesize response
    tts_result = await synthesize_speech(chat_result["response"])

    return {
        "transcript": transcript,
        "ai_response": chat_result["response"],
        "audio_url": tts_result.get("audio_content"),
        "google_services": [
            "Google Cloud Speech-to-Text API",
            "Google Gemini 1.5 Flash API",
            "Google Cloud Text-to-Speech API",
        ],
    }
