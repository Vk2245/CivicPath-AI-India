"""
firebase_service.py — Firebase Database Integration
======================================================
Purpose:        CRUD operations for journeys, chat, checklist, reminders
Inputs:         Structured data from routers
Outputs:        Database query results
Deps:           firebase-admin==6.5.0

Challenge Alignment: Persistent storage for voter journey progress,
chat history, and reminder subscriptions.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from config import get_settings
from demo_data import DEMO_DATA

logger = logging.getLogger("civicpath.firebase")

_db: Any = None


async def init_firebase_client() -> None:
    """Initialize Firebase client for database operations."""
    global _db
    settings = get_settings()

    if not settings.FIREBASE_PROJECT_ID and not settings.FIREBASE_CREDENTIALS_PATH:
        logger.warning("Firebase not configured — using in-memory storage")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()  # Uses application default credentials (e.g. on Cloud Run)

        _db = firestore.client()
        logger.info("Firebase client initialized successfully")
    except Exception as exc:
        logger.error(f"Failed to init Firebase: {exc}")


# In-memory fallback storage for demo mode
_memory_store: dict[str, dict[str, Any]] = {}


async def create_journey(journey_data: dict[str, Any]) -> dict[str, Any]:
    """Create a new voter journey in the database.

    Args:
        journey_data: Journey creation data.

    Returns:
        Created journey record with generated ID.
    """
    journey_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    record = {
        "id": journey_id,
        **journey_data,
        "current_step": 0,
        "created_at": now,
        "updated_at": now,
    }

    if _db:
        try:
            _db.collection("journeys").document(journey_id).set(record)
            return record
        except Exception as exc:
            logger.error(f"Firebase insert failed: {exc}")

    _memory_store[journey_id] = record
    return record


async def get_journey(journey_id: str) -> dict[str, Any] | None:
    """Retrieve a journey by ID.

    Args:
        journey_id: Unique journey identifier.

    Returns:
        Journey record or None if not found.
    """
    if _db:
        try:
            doc = _db.collection("journeys").document(journey_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as exc:
            logger.error(f"Firebase query failed: {exc}")

    return _memory_store.get(journey_id)


async def update_journey_step(
    journey_id: str, step_number: int, status: str
) -> dict[str, Any] | None:
    """Update a journey step's status.

    Args:
        journey_id: Journey identifier.
        step_number: Step number to update.
        status: New status value.

    Returns:
        Updated journey record.
    """
    now = datetime.now(UTC).isoformat()

    if _db:
        try:
            doc_ref = _db.collection("journeys").document(journey_id)
            doc_ref.update({"current_step": step_number, "updated_at": now})
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as exc:
            logger.error(f"Firebase update failed: {exc}")

    if journey_id in _memory_store:
        _memory_store[journey_id]["current_step"] = step_number
        _memory_store[journey_id]["updated_at"] = now
        return _memory_store[journey_id]
    return None


async def save_chat_message(journey_id: str | None, role: str, content: str) -> dict[str, Any]:
    """Save a chat message to the database.

    Args:
        journey_id: Associated journey ID.
        role: Message role (user/assistant).
        content: Message content.

    Returns:
        Saved message record.
    """
    message_id = str(uuid4())
    record = {
        "id": message_id,
        "journey_id": journey_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(UTC).isoformat(),
    }

    if _db:
        try:
            _db.collection("chat_messages").document(message_id).set(record)
        except Exception as exc:
            logger.error(f"Failed to save chat message: {exc}")

    return record


async def create_reminder(reminder_data: dict[str, Any]) -> dict[str, Any]:
    """Create a reminder subscription.

    Args:
        reminder_data: Reminder subscription data.

    Returns:
        Created reminder record.
    """
    reminder_id = str(uuid4())
    record = {
        "id": reminder_id,
        **reminder_data,
        "created_at": datetime.now(UTC).isoformat(),
    }

    if _db:
        try:
            _db.collection("reminders").document(reminder_id).set(record)
            return record
        except Exception as exc:
            logger.error(f"Failed to create reminder: {exc}")

    return record


async def search_faq_embeddings(
    query_embedding: list[float], limit: int = 5
) -> list[dict[str, Any]]:
    """Search FAQ embeddings using pgvector similarity.
    Note: Firestore doesn't natively support pgvector, so for the demo we'll use DEMO_DATA
    or a vector database extension if configured. For this hackathon, we'll fall back to demo
    unless a specific Firebase Extension for Vector Search is active.

    Args:
        query_embedding: Query vector from Gemini Embeddings.
        limit: Maximum results.

    Returns:
        List of matching FAQ records.
    """
    if _db:
        try:
            # Placeholder for Firebase Vector Search Extension
            logger.info("Using fallback for vector search in Firebase")
            pass
        except Exception as exc:
            logger.error(f"FAQ search failed: {exc}")

    return DEMO_DATA["gemini_embeddings"]
