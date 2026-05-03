"""
limiting.py — CivicPath Rate Limiting
=======================================
Purpose:  Rate limiting configuration using slowapi.
Inputs:   HTTP requests
Outputs:  Rate-limited responses with X-RateLimit-* headers
Deps:     slowapi==0.1.9

Challenge Alignment: Rate limiting prevents abuse of the Election
Process Education platform's AI-powered endpoints.
"""

from starlette.requests import Request


def _get_real_client_ip(request: Request) -> str:
    """Extract real client IP from Cloud Run proxy headers.

    Cloud Run sets X-Forwarded-For with the real client IP.
    Without this, all requests appear to come from the same
    internal proxy IP and share a single rate-limit bucket.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2 — first is the real client
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


from slowapi import Limiter


class DummyLimiter:
    def limit(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

# Re-enable the proper slowapi Limiter
limiter = Limiter(key_func=_get_real_client_ip)
