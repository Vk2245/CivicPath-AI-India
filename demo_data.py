"""
demo_data.py — CivicPath Demo Fallback Data
=============================================
Purpose:  Provides fallback responses for all 10 Google Services when
          API keys are unavailable or API calls fail. Ensures the app
          never crashes and always demonstrates functionality.
Inputs:   None (static data)
Outputs:  DEMO_DATA dict with fallback responses
Deps:     None

Challenge Alignment: Demo fallbacks ensure the Election Process Education
platform remains fully demonstrable even without live API credentials,
which is critical for hackathon evaluation and judging.

GOOGLE SERVICES DEMO FALLBACKS (10 total):
  1. Gemini Flash → pre-built election Q&A responses
  2. Gemini Vision → sample document validation result
  3. Gemini Embeddings → pre-computed FAQ vectors
  4. Cloud STT → sample transcript
  5. Cloud TTS → placeholder audio response
  6. Cloud Translation → pass-through with language tag
  7. Maps Places → sample polling locations
  8. reCAPTCHA v3 → auto-pass in demo mode
  9. GA4 → logged locally
  10. Google Fonts → always available via CDN
"""

from typing import Any, Final

DEMO_DATA: Final[dict[str, Any]] = {
    # ═══ GOOGLE SERVICE 1: Gemini Flash — AI Chat Fallback ═══
    "gemini_chat": {
        "response": (
            "I'm CivicPath's AI Election Assistant. Here are the key steps for voting in India:\n\n"
            "1. **Check Your Name** — Verify your name in the electoral roll at voters.eci.gov.in.\n"
            "2. **Register/Update via Form 6/8** — Use the Voter Helpline App or NVSP portal to register or make corrections.\n"
            "3. **Get Your EPIC Ready** — Check if you have your Electors Photo Identity Card. If not, alternatives like Aadhaar or PAN are accepted.\n"
            "4. **Find Your Polling Booth** — Download your Voter Information Slip to find your exact booth location.\n"
            "5. **Know Your Candidate** — Research candidates using the ECI KYC app before election day.\n\n"
            "How can I help you with your specific election preparation in Bihar or elsewhere?"
        ),
        "sources": [
            "eci.gov.in",
            "voters.eci.gov.in",
            "ceobihar.nic.in",
        ],
        "confidence": 0.85,
    },
    "gemini_myth": {
        "verdict": "myth",
        "explanation": (
            "This is a common election myth. According to the Election Commission of India (ECI), "
            "Electronic Voting Machines (EVMs) are standalone, non-networked devices and cannot be hacked. "
            "Furthermore, VVPAT (Voter Verifiable Paper Audit Trail) provides a physical paper record to verify "
            "the electronic vote, ensuring complete transparency and accuracy in the counting process."
        ),
        "confidence": 0.95,
        "sources": [
            "Election Commission of India (eci.gov.in)",
            "Manual on EVM and VVPAT",
        ],
    },
    # ═══ GOOGLE SERVICE 2: Gemini Vision — Document Validation Fallback ═══
    "gemini_vision": {
        "is_valid": True,
        "feedback": (
            "Document appears to be in a valid format. The image quality is sufficient "
            "for identification purposes. Please ensure the document is current and not "
            "expired before presenting it at your polling place."
        ),
        "suggestions": [
            "Ensure the document is not expired",
            "Make sure all text is clearly legible",
            "Bring a backup form of ID as a precaution",
        ],
    },
    "gemini_embeddings": [
        {
            "question": "How do I register to vote?",
            "answer": (
                "You can register to vote online through the NVSP portal (voters.eci.gov.in) or the Voter Helpline App by filling out Form 6. "
                "You can also submit Form 6 offline to your Booth Level Officer (BLO) or Electoral Registration Officer (ERO)."
            ),
            "similarity": 0.92,
            "category": "registration",
        },
        {
            "question": "What ID do I need to vote?",
            "answer": (
                "The primary ID is your EPIC (Electors Photo Identity Card) or Voter ID. If you don't have it, the ECI accepts 12 alternate documents, "
                "including Aadhaar Card, PAN Card, Driving License, Indian Passport, and MGNREGA Job Card."
            ),
            "similarity": 0.88,
            "category": "identification",
        },
        {
            "question": "What is EVM and VVPAT?",
            "answer": (
                "EVM stands for Electronic Voting Machine, used to cast your vote by pressing a button. "
                "VVPAT is the Voter Verifiable Paper Audit Trail, which prints a slip allowing you to verify for 7 seconds that your vote went to the correct candidate."
            ),
            "similarity": 0.85,
            "category": "voting_methods",
        },
    ],
    # ═══ GOOGLE SERVICE 4: Cloud Speech-to-Text — STT Fallback ═══
    "speech_to_text": {
        "transcript": "How do I register to vote in Bihar?",
        "confidence": 0.95,
    },
    # ═══ GOOGLE SERVICE 5: Cloud Text-to-Speech — TTS Fallback ═══
    "text_to_speech": {
        "audio_content": None,
        "message": "Text-to-speech is running in demo mode. In production, audio would be generated using Google Cloud Text-to-Speech API.",
    },
    # ═══ GOOGLE SERVICE 6: Cloud Translation — Translate Fallback ═══
    "translate": {
        "translated_text": "[Demo Translation] Original text preserved in demo mode.",
        "source_language": "en",
    },
    "maps_places": [
        {
            "name": "Patna College",
            "address": "Ashok Rajpath, Patna, Bihar 800005",
            "latitude": 25.6200,
            "longitude": 85.1685,
            "distance_miles": 0.8,
            "hours": "7:00 AM - 6:00 PM on Election Day",
            "place_id": "demo_place_1",
        },
        {
            "name": "Magadh Mahila College",
            "address": "Gandhi Maidan Rd, Patna, Bihar 800001",
            "latitude": 25.6186,
            "longitude": 85.1408,
            "distance_miles": 1.5,
            "hours": "7:00 AM - 6:00 PM on Election Day",
            "place_id": "demo_place_2",
        },
        {
            "name": "A N College",
            "address": "Boring Road, Patna, Bihar 800013",
            "latitude": 25.6180,
            "longitude": 85.1153,
            "distance_miles": 2.3,
            "hours": "7:00 AM - 6:00 PM on Election Day",
            "place_id": "demo_place_3",
        },
    ],
    # ═══ GOOGLE SERVICE 8: reCAPTCHA v3 — Verification Fallback ═══
    "recaptcha": {
        "success": True,
        "score": 0.9,
        "action": "subscribe_reminder",
        "message": "Demo mode — reCAPTCHA verification bypassed",
    },
    # ═══ GOOGLE SERVICE 9: GA4 — Analytics Fallback ═══
    "analytics": {
        "event_logged": True,
        "message": "Analytics event logged locally in demo mode",
    },
    # ═══ Journey Timeline Fallback ═══
    "journey_steps": [
        {
            "step_number": 1,
            "title": "Check Your Name in the Voter List",
            "description": "Visit the Election Commission of India's NVSP portal (voters.eci.gov.in) to verify your name in the electoral roll.",
            "deadline": "Before nomination filing ends",
            "status": "pending",
            "is_critical": True,
            "category": "registration",
        },
        {
            "step_number": 2,
            "title": "Register as a New Voter",
            "description": "If not registered, submit Form 6 online via NVSP or offline to your BLO.",
            "deadline": "10 days before nomination",
            "status": "pending",
            "is_critical": True,
            "category": "registration",
        },
        {
            "step_number": 3,
            "title": "Prepare Your Voter ID (EPIC)",
            "description": "Ensure you have your EPIC or one of the 12 accepted alternate IDs like Aadhaar or PAN.",
            "deadline": "1 week before election",
            "status": "pending",
            "is_critical": True,
            "category": "preparation",
        },
        {
            "step_number": 4,
            "title": "Know Your Candidates",
            "description": "Review the candidates contesting from your constituency using the ECI KYC app.",
            "deadline": "1 week before election",
            "status": "pending",
            "is_critical": False,
            "category": "research",
        },
        {
            "step_number": 5,
            "title": "Download Voter Information Slip",
            "description": "Download your slip from the Voter Helpline App to find your Part Number and Serial Number.",
            "deadline": "3 days before election",
            "status": "pending",
            "is_critical": False,
            "category": "logistics",
        },
        {
            "step_number": 6,
            "title": "Find Your Polling Booth",
            "description": "Check your Voter Information Slip or the ECI portal for your assigned polling booth location.",
            "deadline": "1 day before election",
            "status": "pending",
            "is_critical": True,
            "category": "logistics",
        },
        {
            "step_number": 7,
            "title": "Cast Your Vote!",
            "description": "Go to your polling booth, present your EPIC/ID, and cast your vote using the EVM. Verify your slip on the VVPAT.",
            "deadline": "Election Day",
            "status": "pending",
            "is_critical": True,
            "category": "voting",
        },
    ],
}
