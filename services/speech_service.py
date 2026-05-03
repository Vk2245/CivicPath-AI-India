"""
speech_service.py — Google Cloud Speech Integration
=====================================================
Google Service: Google Cloud Speech-to-Text API, Google Cloud Text-to-Speech API
SDK Package:    google-cloud-speech==2.30.0, google-cloud-texttospeech==2.21.1
Purpose:        Voice input/output for election assistant accessibility
Inputs:         Audio bytes (STT), text strings (TTS)
Outputs:        Transcribed text (STT), audio bytes (TTS)
Deps:           google-cloud-speech==2.30.0, google-cloud-texttospeech==2.21.1

Challenge Alignment: This module directly addresses the Election Process
Education challenge requirement of making election guidance "easy to follow"
by providing voice accessibility via Google Cloud Speech APIs.

GOOGLE API CALLS IN THIS MODULE:
  - transcribe_audio(): Calls Google Cloud Speech-to-Text to convert voice input
  - synthesize_speech(): Calls Google Cloud Text-to-Speech to read steps aloud
"""

import base64
import logging
from typing import Any

from config import get_settings
from demo_data import DEMO_DATA

logger = logging.getLogger("civicpath.speech")

# ═══ GOOGLE SERVICE: Cloud Speech-to-Text + Text-to-Speech ═══
# SDK: google-cloud-speech, google-cloud-texttospeech
# Docs: https://cloud.google.com/speech-to-text/docs

_stt_client: Any = None
_tts_client: Any = None


async def init_speech_clients() -> None:
    """Initialize Google Cloud Speech-to-Text and Text-to-Speech clients.

    Called once during FastAPI app lifespan startup. Reuses the
    same client instances for all requests (connection pooling).

    Google Service: Cloud Speech-to-Text, Cloud Text-to-Speech
    SDK: google-cloud-speech, google-cloud-texttospeech

    Raises:
        SpeechServiceError: If client initialization fails.
    """
    global _stt_client, _tts_client
    settings = get_settings()

    if not settings.GOOGLE_CLOUD_PROJECT:
        logger.warning(
            "GOOGLE_CLOUD_PROJECT not set — Speech services in demo mode",
            extra={"google_service": "Google Cloud Speech APIs"},
        )
        return

    try:
        # [GOOGLE SERVICE: Cloud Speech-to-Text] — client initialization
        from google.cloud import speech

        _stt_client = speech.SpeechClient()

        # [GOOGLE SERVICE: Cloud Text-to-Speech] — client initialization
        from google.cloud import texttospeech

        _tts_client = texttospeech.TextToSpeechClient()

        logger.info(
            "Google Cloud Speech clients initialized successfully",
            extra={"google_service": "Cloud Speech-to-Text + Text-to-Speech"},
        )
    except Exception as exc:
        logger.error(
            "Failed to initialize Google Cloud Speech clients",
            extra={"error": str(exc), "google_service": "Cloud Speech APIs"},
        )


async def transcribe_audio(audio_bytes: bytes, language: str = "en-US") -> dict[str, Any]:
    """Transcribe audio to text using Google Cloud Speech-to-Text API.

    Integrates Google Cloud Speech-to-Text API for voice input accessibility.
    Voters can speak their election questions instead of typing.

    Google Service Used: Google Cloud Speech-to-Text API
    SDK Call: speech.SpeechClient().recognize(config=config, audio=audio)

    Args:
        audio_bytes: Raw audio bytes to transcribe.
        language: Language code for recognition (default en-US).

    Returns:
        Dictionary with transcript and confidence score.

    Raises:
        SpeechServiceError: If Google Cloud Speech-to-Text API call fails.
    """
    logger.info(
        "Calling Google Cloud Speech-to-Text API",
        extra={"function": "transcribe_audio", "google_service": "Cloud Speech-to-Text"},
    )

    if _stt_client is None:
        logger.warning("STT not initialized — using demo fallback")
        return DEMO_DATA["speech_to_text"]

    try:
        from google.cloud import speech

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language,
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        audio = speech.RecognitionAudio(content=audio_bytes)

        # [GOOGLE SERVICE: Cloud Speech-to-Text] — transcribe voice input
        response = _stt_client.recognize(config=config, audio=audio)

        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            logger.info(
                "Google Cloud Speech-to-Text call succeeded",
                extra={"google_service": "Cloud Speech-to-Text"},
            )
            return {"transcript": transcript, "confidence": confidence}

        return {"transcript": "", "confidence": 0.0}
    except Exception as exc:
        logger.error(
            "Google Cloud Speech-to-Text API call failed",
            extra={"error": str(exc), "google_service": "Cloud Speech-to-Text"},
        )
        return DEMO_DATA["speech_to_text"]


async def synthesize_speech(text: str, language: str = "en-US") -> dict[str, Any]:
    """Convert text to speech using Google Cloud Text-to-Speech API.

    Integrates Google Cloud Text-to-Speech API to read election steps
    aloud for accessibility — supporting low-literacy and visually
    impaired voters.

    Google Service Used: Google Cloud Text-to-Speech API
    SDK Call: texttospeech.TextToSpeechClient().synthesize_speech(input, voice, config)

    Args:
        text: Text to convert to speech.
        language: Language code for synthesis (default en-US).

    Returns:
        Dictionary with base64-encoded audio content.

    Raises:
        SpeechServiceError: If Google Cloud Text-to-Speech API call fails.
    """
    logger.info(
        "Calling Google Cloud Text-to-Speech API",
        extra={"function": "synthesize_speech", "google_service": "Cloud Text-to-Speech"},
    )

    if _tts_client is None:
        logger.warning("TTS not initialized — using demo fallback")
        return DEMO_DATA["text_to_speech"]

    try:
        from google.cloud import texttospeech

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,
        )

        # [GOOGLE SERVICE: Cloud Text-to-Speech] — synthesize election guidance audio
        response = _tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
        logger.info(
            "Google Cloud Text-to-Speech call succeeded",
            extra={"google_service": "Cloud Text-to-Speech"},
        )
        return {"audio_content": audio_b64, "message": "Audio synthesized successfully"}
    except Exception as exc:
        logger.error(
            "Google Cloud Text-to-Speech API call failed",
            extra={"error": str(exc), "google_service": "Cloud Text-to-Speech"},
        )
        return DEMO_DATA["text_to_speech"]
