
import time
import functools
from typing import Literal
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.limiter.algorithms import fixed_window, sliding_window, token_bucket
from app.limiter.keys import extract_identifier, build_key, build_sliding_key, build_token_bucket_key
from app.limiter.response import rate_limit_headers, too_many_requests
from app.monitoring.metrics import record_metric, REQUEST_LATENCY
from app.utils.redis_client import get_redis
from app.config import settings

Algorithm = Literal["fixed", "sliding", "token_bucket"]

def rate_limit(
    requests: int,
    window: int = 60,
    by: Literal["ip", "user", "api_key"] = "ip",
    algorithm: Algorithm = "sliding",
    cost: int = 1,
):
    """
    Decorator for FastAPI route functions.

    Usage:
        @app.get("/api/search")
        @rate_limit(requests=100, window=60, by="ip", algorithm="sliding")
        async def search(request: Request):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract Request from args/kwargs
            request: Request = kwargs.get("request") or next(
                (a for a in args if isinstance(a, Request)), None
            )
            if request is None:
                return await func(*args, **kwargs)

            ip = request.client.host

            # ── Blacklist check ──────────────────────────
            if ip in settings.BLACKLISTED_IPS:
                return JSONResponse(
                    status_code=403,
                    content={"error": "Forbidden", "reason": "Blacklisted IP"}
                )

            # ── Whitelist bypass ─────────────────────────
            if ip in settings.WHITELISTED_IPS:
                return await func(*args, **kwargs)

            r = await get_redis()
            identifier = await extract_identifier(request, by)
            endpoint  = request.url.path

            start = time.perf_counter()

            # ── Run chosen algorithm ─────────────────────
            if algorithm == "fixed":
                key    = build_key("ratelimit", identifier, endpoint, window)
                result = await fixed_window(r, key, requests, window)

            elif algorithm == "sliding":
                key    = build_sliding_key(identifier, endpoint)
                result = await sliding_window(r, key, requests, window)

            elif algorithm == "token_bucket":
                key         = build_token_bucket_key(identifier, endpoint)
                refill_rate = requests / window        # tokens / second
                result      = await token_bucket(r, key, requests, refill_rate, cost)

            else:
                result = await sliding_window(
                    r, build_sliding_key(identifier, endpoint), requests, window
                )

            elapsed = time.perf_counter() - start
            REQUEST_LATENCY.labels(algorithm=algorithm).observe(elapsed)

            # ── Record Prometheus metrics ────────────────
            await record_metric(
                endpoint=endpoint,
                algorithm=algorithm,
                allowed=result.allowed,
                count=result.count,
                limit=result.limit,
                identifier_type=by,
            )

            # ── Block if over limit ──────────────────────
            if not result.allowed:
                return too_many_requests(result)

            # ── Continue to route ────────────────────────
            response = await func(*args, **kwargs)

            # Inject rate limit headers into response
            if isinstance(response, Response):
                for k, v in rate_limit_headers(result).items():
                    response.headers[k] = v

            return response

        return wrapper
    return decorator