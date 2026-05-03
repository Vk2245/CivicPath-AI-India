"""
routers/faq.py — FAQ Semantic Search Routes
==============================================
Google Service: Google Gemini Embeddings API
Purpose:        Semantic search across election FAQ knowledge base

GOOGLE API CALLS VIA THIS ROUTER:
  - GET /faq/search → Gemini Embeddings (semantic vector search)
"""

import logging
from typing import Any

from fastapi import APIRouter, Query, Request

from config import RATE_LIMIT_FAQ
from limiting import limiter
from models import FAQSearchResponse
from services.firebase_service import search_faq_embeddings
from services.gemini_service import generate_embedding

logger = logging.getLogger("civicpath.routers.faq")

router = APIRouter(prefix="/faq", tags=["FAQ"])


@router.get("/search", response_model=FAQSearchResponse)
@limiter.limit(RATE_LIMIT_FAQ)
async def search_faq(
    request: Request,
    query: str = Query(..., min_length=3, max_length=500, description="Search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Max results"),
) -> dict[str, Any]:
    """Search election FAQs using semantic similarity.

    Uses Google Gemini Embeddings API to generate query vectors,
    then searches Firebase pgvector for similar FAQ entries.

    Google Service: Google Gemini Embeddings API

    Args:
        request: FastAPI request.
        query: Natural language search query.
        limit: Maximum number of results.

    Returns:
        Semantically matched FAQ results.
    """
    logger.info("Processing FAQ search", extra={"google_service": "Gemini Embeddings"})

    # [GOOGLE SERVICE: Gemini Embeddings] — generate query vector
    query_embedding = await generate_embedding(query)

    # Search pgvector for similar FAQs
    results = await search_faq_embeddings(query_embedding, limit)

    return {
        "results": results,
        "query": query,
        "google_service": "Google Gemini Embeddings API",
    }
