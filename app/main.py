
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.middleware.global_limit import GlobalRateLimitMiddleware
from app.routers import api, admin
from app.utils.redis_client import get_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up Redis connection
    await get_redis()
    yield
    # Shutdown: close Redis pool
    await close_redis()

app = FastAPI(
    title="Rate Limiting System",
    description="Production-grade rate limiting: Fixed, Sliding, Token Bucket",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global DDoS protection (first middleware) ──────────────
app.add_middleware(GlobalRateLimitMiddleware)

# ── Routers ───────────────────────────────────────────────
app.include_router(api.router)
app.include_router(admin.router)

# ── Prometheus metrics endpoint ────────────────────────────
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health", tags=["System"])
async def health():
    r = await get_redis()
    try:
        await r.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {"status": "ok", "redis": "connected" if redis_ok else "error"}
