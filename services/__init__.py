"""
services — CivicPath Service Layer
====================================
Purpose:  Business logic and Google API integration services.
          All services are initialized lazily during FastAPI lifespan.

GOOGLE SERVICES IN THIS PACKAGE:
  1. Google Gemini 1.5 Flash API     → gemini_service.py
  2. Google Gemini Vision API        → gemini_service.py
  3. Google Gemini Embeddings API    → gemini_service.py
  4. Google Cloud Speech-to-Text API → speech_service.py
  5. Google Cloud Text-to-Speech API → speech_service.py
  6. Google Cloud Translation API    → translate_service.py
  7. Google Maps Places API          → maps_service.py
  8. Google reCAPTCHA v3 API         → recaptcha_service.py
  9. Google Analytics 4 API          → analytics_service.py
"""
