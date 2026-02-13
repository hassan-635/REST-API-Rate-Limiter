
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.limiter.algorithms import LimitResult

def rate_limit_headers(result: LimitResult) -> dict:
    return {
        "X-RateLimit-Limit":     str(result.limit),
        "X-RateLimit-Remaining": str(result.remaining),
        "X-RateLimit-Reset":     str(result.reset_at),
        **({"Retry-After": str(result.retry_after)} if not result.allowed else {}),
    }

def too_many_requests(result: LimitResult) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        headers=rate_limit_headers(result),
        content={
            "error":       "Too Many Requests",
            "message":     "Rate limit exceeded. Please slow down.",
            "retry_after": result.retry_after,
            "limit":       result.limit,
            "reset_at":    result.reset_at,
        },
    )