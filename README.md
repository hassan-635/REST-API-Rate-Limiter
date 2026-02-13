# 🛡️ Production Rate Limiting System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitored-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A production-grade, battle-tested rate limiting system built with FastAPI and Redis.**  
Protect your APIs from abuse, brute-force attacks, and DDoS with three powerful algorithms.

[Features](#-features) • [Quick Start](#-quick-start) • [Algorithms](#-algorithms) • [Usage](#-usage) • [Admin API](#-admin-api) • [Monitoring](#-monitoring)

</div>

---

## 🌟 Why This Project?

Every public API faces the same threats:
- 🤖 **Bots** hammering your endpoints thousands of times per second
- 🔐 **Brute-force attacks** trying thousands of passwords on your login page
- 💸 **Cost explosions** from abusive API consumers
- 🌊 **DDoS attacks** that bring your service down entirely

This system provides **three industry-standard rate limiting algorithms** with a clean decorator API, Redis-backed persistence, Prometheus metrics, Grafana dashboards, and Slack alerting — everything you need to protect a production API.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔢 **3 Algorithms** | Fixed Window, Sliding Window, Token Bucket |
| 🎨 **Decorator API** | One line to protect any route: `@rate_limit(...)` |
| 🎯 **Smart Identification** | Limit by IP, JWT User ID, or API Key |
| 🌍 **Global DDoS Protection** | Middleware-level 10,000 req/min per IP |
| ⚪ **Whitelist / Blacklist** | Bypass trusted IPs, permanently block abusers |
| 💰 **Cost-based Limiting** | Expensive endpoints consume more tokens |
| 🏷️ **Tiered Plans** | Free / Pro / Enterprise limits out of the box |
| 📊 **Prometheus Metrics** | Real-time counters, histograms, gauges |
| 📈 **Grafana Dashboards** | Beautiful visualizations with zero setup |
| 🔔 **Slack Alerts** | Early warning at 80% usage threshold |
| 🛠️ **Admin REST API** | Check status, reset limits, view stats |
| 🐳 **Docker Ready** | One command to spin up the entire stack |
| ⚡ **Lua Scripts** | Atomic Redis operations — zero race conditions |
| 📝 **RFC 6585 Compliant** | Standard `Retry-After` and rate limit headers |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Incoming Request                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              GlobalRateLimitMiddleware                       │
│         (DDoS Protection: 10,000 req/min per IP)            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  @rate_limit Decorator                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ Blacklist   │  │  Whitelist   │  │   Identify User    │ │
│  │   Check     │  │   Bypass     │  │  (IP/User/API Key) │ │
│  └─────────────┘  └──────────────┘  └────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Redis Rate Limiter                         │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │ Fixed Window │ │Sliding Window│ │   Token Bucket     │  │
│  │  (INCR/TTL)  │ │  (Sorted Set)│ │   (Lua Script)     │  │
│  └──────────────┘ └──────────────┘ └────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
               ┌──────────┴──────────┐
               │                     │
               ▼                     ▼
        ✅ Allowed              ❌ Blocked
        Route Handler          429 Response
        + Rate Headers         + Retry-After
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Prometheus + Grafana + Slack                 │
│              (Metrics, Dashboards, Alerts)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
rate_limiter/
├── app/
│   ├── main.py                  # FastAPI app, middleware, routers
│   ├── config.py                # All configuration (env vars)
│   ├── dependencies.py          # Admin auth dependency
│   │
│   ├── limiter/
│   │   ├── __init__.py
│   │   ├── algorithms.py        # Fixed, Sliding, Token Bucket
│   │   ├── decorator.py         # @rate_limit decorator
│   │   ├── keys.py              # Redis key generation
│   │   └── response.py          # 429 response builder
│   │
│   ├── middleware/
│   │   └── global_limit.py      # DDoS protection middleware
│   │
│   ├── routers/
│   │   ├── api.py               # Protected example routes
│   │   └── admin.py             # Admin management endpoints
│   │
│   ├── monitoring/
│   │   └── metrics.py           # Prometheus metrics + Slack alerts
│   │
│   └── utils/
│       ├── auth.py              # JWT utilities
│       └── redis_client.py      # Async Redis connection pool
│
├── tests/
│   ├── test_fixed_window.py
│   ├── test_sliding_window.py
│   ├── test_token_bucket.py
│   └── test_admin.py
│
├── docker-compose.yml           # Full stack: API + Redis + Prometheus + Grafana
├── Dockerfile
├── prometheus.yml               # Prometheus scrape config
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rate-limiter.git
cd rate-limiter
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Global Limits
GLOBAL_RATE_LIMIT=10000
GLOBAL_WINDOW=60

# Whitelist (comma-separated)
WHITELISTED_IPS=["127.0.0.1","::1"]

# Blacklist (comma-separated)
BLACKLISTED_IPS=[]

# Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_THRESHOLD=0.80
```

### 3. Start the Full Stack

```bash
docker compose up -d
```

This starts:
| Service | URL | Purpose |
|---|---|---|
| **FastAPI** | http://localhost:8000 | Main API |
| **Redis** | localhost:6379 | Rate limit storage |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3000 | Dashboards (admin/admin) |

### 4. Test It

```bash
# Successful request
curl http://localhost:8000/api/search?q=hello
# → 200 OK
# Headers: X-RateLimit-Limit: 100, X-RateLimit-Remaining: 99

# Exceed the limit (run this in a loop)
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" \
  http://localhost:8000/api/auth/login; done
# → 200 200 200 200 200 429 429 429 429 429

# Check health
curl http://localhost:8000/health
# → {"status": "ok", "redis": "connected"}
```

---

## 🧠 Algorithms

### 1. 🔵 Fixed Window

The simplest approach. Time is divided into fixed buckets. Each bucket has its own counter.

```
Limit: 5 requests per 60 seconds

Timeline:
│◄──── Window 1 ────►│◄──── Window 2 ────►│
│  ✅  ✅  ✅  ✅  ✅ │  ✅  ✅  ✅  ✅  ✅ │
│  1   2   3   4   5  │  1   2   3   4   5  │
│0s              60s  │60s            120s  │
```

**⚠️ Known Issue — Boundary Burst:**
```
│ ... 58s: req5 ✅ │ 60s: req1 req2 req3 req4 req5 ✅ │
                     ← 10 requests in 2 seconds!
```

**Redis Operations:**
```
INCR  ratelimit:IP:endpoint:bucket  → increment counter
EXPIRE key 60                        → auto-expire after window
```

**Best for:** Simple counters, internal APIs, non-critical endpoints.

---

### 2. 🟢 Sliding Window

Uses a Redis Sorted Set where each request's timestamp is stored as the score. At every request, old entries are removed and remaining entries are counted.

```
Limit: 5 requests per 60 seconds
Current time: 1000s

Sorted Set:
  Score   │ Member
  940.1   │ req_a   ← too old (< 940), removed!
  945.2   │ req_b   ← too old, removed!
  960.5   │ req_c   ← ✅ within window
  975.8   │ req_d   ← ✅ within window
  990.1   │ req_e   ← ✅ within window
  ────────────────
  Count = 3 → below limit → ✅ ALLOWED
```

**Redis Operations:**
```
ZADD   key timestamp "member"         → add request
ZREMRANGEBYSCORE key -inf (now-60s)   → remove old entries
ZCARD  key                             → count = ?
EXPIRE key window+1                    → cleanup TTL
```

**Best for:** Login endpoints, API rate limits, payment APIs — anywhere accuracy matters.

---

### 3. 🟡 Token Bucket

Imagine a bucket that starts full of tokens. Each request consumes one (or more) tokens. Tokens are refilled at a constant rate. Allows short bursts while enforcing long-term limits.

```
Capacity: 10 tokens
Refill:   1 token/second

t=0s:  [🪙🪙🪙🪙🪙🪙🪙🪙🪙🪙] = 10 tokens (full)

Burst of 8 requests:
t=0s:  [🪙🪙] = 2 tokens left

t=3s:  Refill 3 tokens → [🪙🪙🪙🪙🪙] = 5 tokens
t=4s:  Request → [🪙🪙🪙🪙] = 4 tokens ✅

t=0s + 0 tokens: ❌ BLOCKED → retry_after = 1s
```

**Cost-based requests (upload = 10 tokens):**
```python
@rate_limit(requests=50, window=3600, algorithm="token_bucket", cost=10)
async def upload_file(request: Request): ...
# Uploading a file costs 10x more than a normal GET request
```

**Lua Script (Atomic Operation):**
```lua
-- Read tokens + last_refill
-- Calculate refill based on elapsed time
-- Deduct cost if tokens available
-- Write back atomically
-- No race conditions ✓
```

**Best for:** APIs with burst tolerance, file upload endpoints, expensive operations.

---

### Algorithm Comparison

| Scenario | Recommended Algorithm |
|---|---|
| Simple counter, maximum speed | ✅ Fixed Window |
| Accurate, no boundary burst | ✅ Sliding Window |
| Allow bursts, smooth long-term | ✅ Token Bucket |
| Login / Auth (brute force) | ✅ Sliding Window |
| File upload (expensive ops) | ✅ Token Bucket (cost > 1) |
| Internal microservices | ✅ Fixed Window |
| Public API endpoints | ✅ Sliding Window |

---

## 💻 Usage

### Basic Usage

```python
from fastapi import FastAPI, Request
from app.limiter.decorator import rate_limit

app = FastAPI()

@app.get("/api/search")
@rate_limit(requests=100, window=60, by="ip", algorithm="sliding")
async def search(request: Request, q: str = ""):
    return {"results": []}
```

### All Decorator Options

```python
@rate_limit(
    requests=100,               # Max requests allowed
    window=60,                  # Time window in seconds
    by="ip",                    # "ip" | "user" | "api_key"
    algorithm="sliding",        # "fixed" | "sliding" | "token_bucket"
    cost=1,                     # Tokens per request (token_bucket only)
)
```

### Per-Endpoint Configuration

```python
# 🔐 Login — strict brute-force protection
@app.post("/api/auth/login")
@rate_limit(requests=5, window=60, by="ip", algorithm="sliding")
async def login(request: Request): ...

# 🔍 Search — moderate per-IP limit
@app.get("/api/search")
@rate_limit(requests=100, window=60, by="ip", algorithm="sliding")
async def search(request: Request): ...

# 📦 Data API — generous per-user limit
@app.get("/api/data")
@rate_limit(requests=1000, window=3600, by="user", algorithm="token_bucket")
async def get_data(request: Request): ...

# 📤 Upload — cost-based (consumes 10 tokens)
@app.post("/api/upload")
@rate_limit(requests=50, window=3600, by="user",
            algorithm="token_bucket", cost=10)
async def upload(request: Request): ...

# 🔑 External API — API key based
@app.get("/api/external")
@rate_limit(requests=500, window=3600, by="api_key", algorithm="sliding")
async def external(request: Request): ...
```

### Tiered Plans (SaaS)

```python
TIER_LIMITS = {
    "free":       {"requests": 10,        "window": 3600},
    "pro":        {"requests": 100,       "window": 3600},
    "enterprise": {"requests": 999999999, "window": 3600},
}

@app.get("/api/data")
async def get_data(request: Request):
    # Read tier from JWT payload
    tier   = request.state.user.get("tier", "free")
    limits = TIER_LIMITS[tier]

    # Apply dynamically (use in middleware or service layer)
    ...
```

---

## 📬 Response Format

### ✅ Successful Request

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1234567890
```

### ❌ Rate Limited (429)

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 42

{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please slow down.",
  "retry_after": 42,
  "limit": 100,
  "reset_at": 1234567890
}
```

### 🚫 Blacklisted IP (403)

```http
HTTP/1.1 403 Forbidden

{
  "error": "Forbidden",
  "reason": "Blacklisted IP"
}
```

---

## 🛠️ Admin API

All admin endpoints require a valid **Admin JWT token** in the `Authorization` header.

### Check IP Status

```bash
GET /admin/ratelimit/{ip}

curl -H "Authorization: Bearer <admin_token>" \
     http://localhost:8000/admin/ratelimit/192.168.1.100
```

```json
{
  "ip": "192.168.1.100",
  "keys_found": 2,
  "statuses": [
    {
      "key": "sliding:192.168.1.100:/api/search",
      "type": "sliding_window",
      "count": 87,
      "ttl": 34
    },
    {
      "key": "ratelimit:192.168.1.100:/api/auth/login:1234",
      "type": "fixed_window",
      "count": 3,
      "ttl": 18
    }
  ]
}
```

### Reset Rate Limits

```bash
# Reset specific IP
POST /admin/ratelimit/reset?ip=192.168.1.100

# Reset specific user
POST /admin/ratelimit/reset?user_id=user_abc123

curl -X POST -H "Authorization: Bearer <admin_token>" \
     "http://localhost:8000/admin/ratelimit/reset?ip=192.168.1.100"
```

```json
{
  "message": "Cleared 3 rate limit keys"
}
```

### View Global Statistics

```bash
GET /admin/ratelimit/stats/overview

curl -H "Authorization: Bearer <admin_token>" \
     http://localhost:8000/admin/ratelimit/stats/overview
```

```json
{
  "timestamp": 1234567890,
  "active_fixed_windows": 142,
  "active_sliding_windows": 89,
  "active_token_buckets": 34,
  "active_global_limits": 201,
  "total_tracked_keys": 466
}
```

---

## 📊 Monitoring

### Prometheus Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `rate_limit_hits_total` | Counter | `endpoint`, `algorithm`, `status` | Total requests checked |
| `rate_limit_blocks_total` | Counter | `endpoint`, `identifier_type` | Total blocked requests |
| `rate_limit_usage_ratio` | Gauge | `endpoint` | Current usage (0.0 - 1.0) |
| `rate_limit_check_duration_seconds` | Histogram | `algorithm` | Time spent in rate limit check |

View raw metrics:
```bash
curl http://localhost:8000/metrics
```

```
# HELP rate_limit_hits_total Total rate limit checks
# TYPE rate_limit_hits_total counter
rate_limit_hits_total{endpoint="/api/search",algorithm="sliding",status="allowed"} 1523.0
rate_limit_hits_total{endpoint="/api/auth/login",algorithm="sliding",status="blocked"} 47.0

# HELP rate_limit_usage_ratio Current usage ratio
# TYPE rate_limit_usage_ratio gauge
rate_limit_usage_ratio{endpoint="/api/search"} 0.73
```

### Grafana Dashboard

1. Open Grafana: http://localhost:3000 (admin / admin)
2. Add Prometheus datasource: `http://prometheus:9090`
3. Import dashboard — create panels for:
   - **Request Rate** — `rate(rate_limit_hits_total[1m])`
   - **Block Rate** — `rate(rate_limit_blocks_total[1m])`
   - **Usage Ratio** — `rate_limit_usage_ratio`
   - **Latency** — `histogram_quantile(0.99, rate_limit_check_duration_seconds_bucket)`

### Slack Alerts

When any endpoint reaches **80% of its limit**, a Slack notification is sent automatically:

```
⚠️ Rate Limit Warning
Endpoint `/api/search` is at 83% capacity (83/100 requests).
```

Configure in `.env`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/XXXX
ALERT_THRESHOLD=0.80
```

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_PASSWORD` | `""` | Redis password (empty = no auth) |
| `SECRET_KEY` | — | JWT signing secret **(change this!)** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `GLOBAL_RATE_LIMIT` | `10000` | Global DDoS limit (req/window) |
| `GLOBAL_WINDOW` | `60` | Global window in seconds |
| `WHITELISTED_IPS` | `["127.0.0.1"]` | IPs that bypass all limits |
| `BLACKLISTED_IPS` | `[]` | IPs permanently blocked |
| `SLACK_WEBHOOK_URL` | `""` | Slack webhook for alerts |
| `ALERT_THRESHOLD` | `0.80` | Usage ratio to trigger alert |

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_sliding_window.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Example Test

```python
# tests/test_sliding_window.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_rate_limit_blocks_after_limit():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 5 allowed requests
        for _ in range(5):
            response = await client.get("/api/auth/login")
            assert response.status_code != 429

        # 6th request should be blocked
        response = await client.get("/api/auth/login")
        assert response.status_code == 429
        assert "retry_after" in response.json()
        assert response.headers["X-RateLimit-Remaining"] == "0"
```

---

## 🐳 Docker Reference

```bash
# Start full stack
docker compose up -d

# View logs
docker compose logs -f api
docker compose logs -f redis

# Stop everything
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Redis CLI (debug)
docker compose exec redis redis-cli

# Check keys in Redis
docker compose exec redis redis-cli KEYS "*"

# Monitor live Redis commands
docker compose exec redis redis-cli MONITOR
```

---

## 🔒 Security Considerations

| Consideration | Implementation |
|---|---|
| **Atomic operations** | Lua scripts prevent race conditions |
| **IP Spoofing** | X-Forwarded-For validation |
| **Admin protection** | JWT role-based access |
| **Redis auth** | Password via `REDIS_PASSWORD` env |
| **Token storage** | No sensitive data in Redis keys |
| **Distributed systems** | Works with Redis Cluster |

### For Production

```bash
# Generate a strong secret key
openssl rand -hex 32

# Use Redis with password
REDIS_PASSWORD=your-strong-redis-password

# Run behind Nginx/Traefik (set X-Forwarded-For)
# Use Redis Sentinel or Cluster for HA
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/rate-limiter.git
cd rate-limiter

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis only (for local dev)
docker compose up redis -d

# Run with hot reload
uvicorn app.main:app --reload --port 8000
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [Redis](https://redis.io/) — In-memory data store
- [Prometheus](https://prometheus.io/) — Metrics collection
- [Grafana](https://grafana.com/) — Metrics visualization
- [redis-py](https://github.com/redis/redis-py) — Python Redis client

---

<div align="center">

**Built with ❤️ for the security-conscious developer**

⭐ Star this repo if it helped you • 🐛 [Report a Bug](issues) • 💡 [Request a Feature](issues)

</div>