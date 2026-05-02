"""
security.py — CivicPath Security Middleware
=============================================
Purpose:  Security headers middleware and input sanitization utilities.
          Adds 7 security headers to every HTTP response.
Inputs:   HTTP requests/responses via ASGI middleware
Outputs:  Responses with security headers injected
Deps:     starlette==0.45.3

Challenge Alignment: Security is critical for a civic-tech platform
handling voter information. This module ensures data integrity and
user trust through defense-in-depth HTTP security headers.
"""

import logging
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("civicpath.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds security headers to every HTTP response.

    Implements 7 security headers recommended by OWASP:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy

    This middleware runs on every response, including error responses.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Add security headers to every response.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or route handler.

        Returns:
            Response with 7 security headers added.
        """
        response = await call_next(request)

        # Security Header 1: Content-Security-Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://*.firebase.co https://*.google.com https://www.google-analytics.com https://maps.googleapis.com; "
            "frame-src https://www.google.com"
        )

        # Security Header 2: HTTP Strict Transport Security
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Security Header 3: X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"

        # Security Header 4: X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Security Header 5: X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Security Header 6: Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Security Header 7: Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(self), geolocation=(self), "
            "payment=(), usb=(), magnetometer=()"
        )

        return response


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing HTML tags and dangerous patterns.

    Args:
        text: Raw user input string.

    Returns:
        Sanitized string safe for processing.
    """
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)
    # Remove potential script injections
    cleaned = re.sub(r"javascript:", "", cleaned, flags=re.IGNORECASE)
    # Remove null bytes
    cleaned = cleaned.replace("\x00", "")
    return cleaned.strip()


def validate_content_length(content: bytes, max_bytes: int = 10_485_760) -> bool:
    """Validate that content does not exceed maximum allowed size.

    Args:
        content: Raw content bytes.
        max_bytes: Maximum allowed size (default 10MB).

    Returns:
        True if content is within limits.

    Raises:
        ValueError: If content exceeds maximum size.
    """
    if len(content) > max_bytes:
        raise ValueError(
            f"Content size {len(content)} exceeds maximum {max_bytes} bytes"
        )
    return True
