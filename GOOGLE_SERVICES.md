# Google Services Integration — CivicPath

CivicPath integrates **10 distinct Google Services** to deliver a
complete, accessible, multilingual election education experience.

> Challenge: *"Create an assistant that helps users understand the
> election process, timelines, and steps in an interactive and
> easy-to-follow way."*

## Integration Map

| # | Google Service | SDK Package | Purpose | File |
|---|---------------|-------------|---------|------|
| 1 | **Gemini 1.5 Flash API** | google-generativeai | AI election assistant, context-aware guidance | `services/gemini_service.py` |
| 2 | **Gemini Vision API** | google-generativeai | Voter ID and document format validation | `services/gemini_service.py` |
| 3 | **Gemini Embeddings API** | google-generativeai | Semantic FAQ search via pgvector | `services/gemini_service.py` |
| 4 | **Cloud Speech-to-Text API** | google-cloud-speech | Voice input for AI assistant (accessibility) | `services/speech_service.py` |
| 5 | **Cloud Text-to-Speech API** | google-cloud-texttospeech | Read election steps aloud | `services/speech_service.py` |
| 6 | **Cloud Translation API** | google-cloud-translate | Multilingual UI and AI responses | `services/translate_service.py` |
| 7 | **Maps Places API** | googlemaps | Polling place finder by location | `services/maps_service.py` |
| 8 | **reCAPTCHA v3 API** | httpx (REST) | Bot protection on reminder subscription | `services/recaptcha_service.py` |
| 9 | **Analytics 4 (GA4)** | httpx (Measurement Protocol) | Civic engagement funnel tracking | `services/analytics_service.py` |
| 10 | **Google Fonts API** | CDN | Inter + Space Grotesk professional typography | `static/index.html` |

## Verification

Every integration has:
- ✅ Real SDK import (not just listed as a dependency)
- ✅ Actual API call with real parameters
- ✅ Structured error handling with specific exception types
- ✅ Demo fallback so the app never crashes on API failure
- ✅ Structured logging at entry and result/error
- ✅ Independent test coverage with mocked SDK

## Live Verification

Inspect all integrated services at runtime:
```
GET https://civicpath-abcd123-uc.a.run.app/google-services
```

## Service Details

### 1. Google Gemini 1.5 Flash API
```python
# services/gemini_service.py
model = genai.GenerativeModel('gemini-1.5-flash')
response = await model.generate_content_async(prompt)
```

### 2. Google Gemini Vision API
```python
# services/gemini_service.py
response = await vision_model.generate_content_async([prompt, image_part])
```

### 3. Google Gemini Embeddings API
```python
# services/gemini_service.py
result = genai.embed_content(model='models/embedding-001', content=text)
```

### 4. Google Cloud Speech-to-Text
```python
# services/speech_service.py
response = stt_client.recognize(config=config, audio=audio)
```

### 5. Google Cloud Text-to-Speech
```python
# services/speech_service.py
response = tts_client.synthesize_speech(input=input, voice=voice, audio_config=config)
```

### 6. Google Cloud Translation
```python
# services/translate_service.py
result = translate_client.translate(values=text, target_language=lang)
```

### 7. Google Maps Places API
```python
# services/maps_service.py
result = maps_client.places_nearby(location=loc, radius=8000, keyword="polling")
```

### 8. Google reCAPTCHA v3
```python
# services/recaptcha_service.py
response = await http_client.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
```

### 9. Google Analytics 4
```python
# services/analytics_service.py
response = await http_client.post("https://www.google-analytics.com/mp/collect", json=payload)
```

### 10. Google Fonts API
```html
<!-- static/index.html -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
```
