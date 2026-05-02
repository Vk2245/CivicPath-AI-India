"""
google_services_registry.py
============================
Purpose:  Manifest of all Google Services integrated into CivicPath.
Inputs:   None (static registry)
Outputs:  GOOGLE_SERVICES dict for /services endpoint + README
Deps:     None

GOOGLE SERVICES INTEGRATED (10 total):
  1. Google Gemini 1.5 Flash API
  2. Google Gemini Vision API
  3. Google Gemini Embeddings API
  4. Google Cloud Speech-to-Text API
  5. Google Cloud Text-to-Speech API
  6. Google Cloud Translation API
  7. Google Maps Places API
  8. Google reCAPTCHA v3 API
  9. Google Analytics 4 (Measurement Protocol)
  10. Google Fonts API
"""

from typing import Final

GOOGLE_SERVICES: Final[dict[str, dict[str, str]]] = {
    "gemini_flash": {
        "name": "Google Gemini 1.5 Flash API",
        "purpose": "AI-powered election assistant and myth-busting engine",
        "sdk_package": "google-generativeai",
        "sdk_call": "genai.GenerativeModel('gemini-1.5-flash').generate_content()",
        "service_file": "services/gemini_service.py",
        "router_file": "routers/chat.py",
        "env_var": "GEMINI_API_KEY",
        "google_service_type": "AI / Generative AI",
    },
    "gemini_vision": {
        "name": "Google Gemini Vision API",
        "purpose": "Document image validation for voter ID and registration forms",
        "sdk_package": "google-generativeai",
        "sdk_call": "genai.GenerativeModel('gemini-1.5-flash').generate_content([image, prompt])",
        "service_file": "services/gemini_service.py",
        "router_file": "routers/checklist.py",
        "env_var": "GEMINI_API_KEY",
        "google_service_type": "AI / Vision",
    },
    "gemini_embeddings": {
        "name": "Google Gemini Embeddings API",
        "purpose": "Semantic vector search for election FAQ knowledge base",
        "sdk_package": "google-generativeai",
        "sdk_call": "genai.embed_content(model='models/embedding-001', content=text)",
        "service_file": "services/gemini_service.py",
        "router_file": "routers/faq.py",
        "env_var": "GEMINI_API_KEY",
        "google_service_type": "AI / Embeddings",
    },
    "cloud_speech_to_text": {
        "name": "Google Cloud Speech-to-Text API",
        "purpose": "Voice input for accessibility",
        "sdk_package": "google-cloud-speech",
        "sdk_call": "speech.SpeechClient().recognize(config, audio)",
        "service_file": "services/speech_service.py",
        "router_file": "routers/chat.py",
        "env_var": "GOOGLE_CLOUD_PROJECT",
        "google_service_type": "AI / Speech",
    },
    "cloud_text_to_speech": {
        "name": "Google Cloud Text-to-Speech API",
        "purpose": "Read election steps aloud for accessibility",
        "sdk_package": "google-cloud-texttospeech",
        "sdk_call": "texttospeech.TextToSpeechClient().synthesize_speech(input, voice, config)",
        "service_file": "services/speech_service.py",
        "router_file": "routers/journey.py",
        "env_var": "GOOGLE_CLOUD_PROJECT",
        "google_service_type": "AI / Speech",
    },
    "google_translate": {
        "name": "Google Cloud Translation API",
        "purpose": "Multilingual election guidance — 10+ languages",
        "sdk_package": "google-cloud-translate",
        "sdk_call": "TranslationServiceClient().translate_text(request)",
        "service_file": "services/translate_service.py",
        "router_file": "routers/translate.py",
        "env_var": "GOOGLE_CLOUD_PROJECT",
        "google_service_type": "AI / Translation",
    },
    "google_maps_places": {
        "name": "Google Maps Places API",
        "purpose": "Find nearby polling places",
        "sdk_package": "googlemaps",
        "sdk_call": "googlemaps.Client(key).places_nearby(location, radius, type)",
        "service_file": "services/maps_service.py",
        "router_file": "routers/maps.py",
        "env_var": "GOOGLE_MAPS_API_KEY",
        "google_service_type": "Maps / Location",
    },
    "google_recaptcha_v3": {
        "name": "Google reCAPTCHA v3 API",
        "purpose": "Bot protection on reminder subscription",
        "sdk_package": "httpx (REST call to Google reCAPTCHA API)",
        "sdk_call": "POST https://www.google.com/recaptcha/api/siteverify",
        "service_file": "services/recaptcha_service.py",
        "router_file": "routers/reminders.py",
        "env_var": "RECAPTCHA_SECRET_KEY",
        "google_service_type": "Security / Bot Protection",
    },
    "google_analytics_4": {
        "name": "Google Analytics 4 (GA4) — Measurement Protocol",
        "purpose": "Track civic engagement funnel",
        "sdk_package": "httpx (Measurement Protocol REST API) + gtag.js",
        "sdk_call": "POST https://www.google-analytics.com/mp/collect",
        "service_file": "services/analytics_service.py",
        "router_file": "routers/journey.py",
        "env_var": "GA4_MEASUREMENT_ID, GA4_API_SECRET",
        "google_service_type": "Analytics",
    },
    "google_fonts": {
        "name": "Google Fonts API",
        "purpose": "Inter + Space Grotesk typography",
        "sdk_package": "CDN (fonts.googleapis.com)",
        "sdk_call": "<link href='https://fonts.googleapis.com/css2?family=Inter'/>",
        "service_file": "static/index.html",
        "router_file": "N/A (frontend CDN)",
        "env_var": "N/A",
        "google_service_type": "Design / Typography",
    },
}

GOOGLE_SERVICES_COUNT: Final[int] = len(GOOGLE_SERVICES)  # 10
