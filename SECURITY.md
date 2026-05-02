# Security Policy — CivicPath

## Threat Model

| Threat | Mitigation | Implementation |
|--------|-----------|----------------|
| XSS (Cross-Site Scripting) | HTML sanitization on all user inputs | `models.py:strip_html_tags()` validator |
| CSRF | SameSite cookies + CORS restriction | `main.py` CORS middleware |
| SQL Injection | Parameterized queries via Firebase SDK | `firebase_service.py` |
| Bot Abuse | Google reCAPTCHA v3 on sensitive endpoints | `recaptcha_service.py` |
| Rate Limiting | slowapi per-IP rate limits | `limiting.py` + router decorators |
| Clickjacking | X-Frame-Options: DENY | `security.py` middleware |
| MIME Sniffing | X-Content-Type-Options: nosniff | `security.py` middleware |
| Transport Security | HSTS with preload | `security.py` middleware |
| Prompt Injection | System prompt sanitization + input limits | `gemini_service.py` |
| Data Access | Firebase Row Level Security (RLS) | `firebase/migrations/` |

## Security Headers (7 total)

Every HTTP response includes:
1. `Content-Security-Policy` — restricts resource loading
2. `Strict-Transport-Security` — enforces HTTPS
3. `X-Frame-Options: DENY` — prevents clickjacking
4. `X-Content-Type-Options: nosniff` — prevents MIME sniffing
5. `X-XSS-Protection: 1; mode=block` — legacy XSS filter
6. `Referrer-Policy: strict-origin-when-cross-origin` — referrer control
7. `Permissions-Policy` — restricts browser features

## Rate Limits

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/journey/start` | 10/min | Prevent journey spam |
| `/chat` | 20/min | Protect Gemini API quota |
| `/reminders/subscribe` | 5/min | Prevent email spam |
| `/translate` | 30/min | Protect Translation API |
| `/faq/search` | 30/min | Protect Embeddings API |

## Reporting Vulnerabilities

Please email security issues to: security@civicpath.app

We will acknowledge within 48 hours and provide a fix timeline within 7 days.
