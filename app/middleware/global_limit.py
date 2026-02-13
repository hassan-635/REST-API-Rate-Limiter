
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.redis_client import get_redis
from app.limiter.algorithms import fixed_window
from app.config import settings

class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global DDoS protection: 10,000 req/min per IP.
    Applied before route handlers.
    """
    async def dispatch(self, request: Request, call_next):
        # Skip health/metrics endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        ip = request.client.host
        if ip in settings.BLACKLISTED_IPS:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden"}
            )
        if ip in settings.WHITELISTED_IPS:
            return await call_next(request)

        r      = await get_redis()
        bucket = int(time.time()) // settings.GLOBAL_WINDOW
        key    = f"global:{ip}:{bucket}"
        result = await fixed_window(
            r, key,
            settings.GLOBAL_RATE_LIMIT,
            settings.GLOBAL_WINDOW
        )

        if not result.allowed:
            return JSONResponse(
                status_code=429,
                headers={
                    "X-RateLimit-Limit":     str(result.limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After":           str(result.retry_after),
                },
                content={
                    "error":       "Global rate limit exceeded",
                    "retry_after": result.retry_after,
                }
            )

        return await call_next(request)
