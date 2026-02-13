
from fastapi import APIRouter, Request
from app.limiter.decorator import rate_limit

router = APIRouter(prefix="/api", tags=["API"])

# ── Auth: strict brute-force protection ───────────────────
@router.post("/auth/login")
@rate_limit(requests=5, window=60, by="ip", algorithm="sliding")
async def login(request: Request):
    return {"message": "Login endpoint"}

@router.post("/auth/register")
@rate_limit(requests=3, window=60, by="ip", algorithm="fixed")
async def register(request: Request):
    return {"message": "Register endpoint"}

# ── Search: moderate limit ─────────────────────────────────
@router.get("/search")
@rate_limit(requests=100, window=60, by="ip", algorithm="sliding")
async def search(request: Request, q: str = ""):
    return {"query": q, "results": []}

# ── Data: generous limit per authenticated user ────────────
@router.get("/data")
@rate_limit(requests=1000, window=3600, by="user", algorithm="token_bucket")
async def get_data(request: Request):
    return {"data": [1, 2, 3, 4, 5]}

# ── Upload: cost-based (each upload costs 10 tokens) ──────
@router.post("/upload")
@rate_limit(requests=50, window=3600, by="user",
            algorithm="token_bucket", cost=10)
async def upload(request: Request):
    return {"message": "File uploaded"}

# ── API key based ──────────────────────────────────────────
@router.get("/external")
@rate_limit(requests=500, window=3600, by="api_key", algorithm="sliding")
async def external_api(request: Request):
    return {"message": "External API response"}
