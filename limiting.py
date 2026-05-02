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

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global rate limiter — keyed by client IP
limiter = Limiter(key_func=get_remote_address)
