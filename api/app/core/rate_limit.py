"""Shared slowapi rate limiter for brute-force / credential-stuffing protection.

Counters are kept in-memory (per API process), which is sufficient for the single-instance
deployment. The limiter keys on the client IP via `get_remote_address`, which reads
`request.client.host`; behind Traefik that is only the real client IP when uvicorn runs with
`--proxy-headers` (see docker-compose.yml / Dockerfile), otherwise it would be the proxy's IP.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.rate_limit_enabled,
    # No global default limit; limits are applied per-endpoint via @limiter.limit(...).
    default_limits=[],
    # Header injection (X-RateLimit-*) would require a `response: Response` param on every
    # limited endpoint; the 429 handler still returns a Retry-After header on block.
    headers_enabled=False,
)
