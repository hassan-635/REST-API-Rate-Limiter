
from prometheus_client import Counter, Histogram, Gauge
import httpx
from app.config import settings

# Prometheus metrics
RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Total rate limit checks",
    ["endpoint", "algorithm", "status"]    # status: allowed/blocked
)
RATE_LIMIT_BLOCKS = Counter(
    "rate_limit_blocks_total",
    "Total rate limit blocks",
    ["endpoint", "identifier_type"]
)
RATE_LIMIT_USAGE = Gauge(
    "rate_limit_usage_ratio",
    "Current usage ratio (count/limit)",
    ["endpoint"]
)
REQUEST_LATENCY = Histogram(
    "rate_limit_check_duration_seconds",
    "Time spent in rate limit check",
    ["algorithm"]
)

async def record_metric(
    endpoint: str,
    algorithm: str,
    allowed: bool,
    count: int,
    limit: int,
    identifier_type: str = "ip",
):
    status = "allowed" if allowed else "blocked"
    RATE_LIMIT_HITS.labels(
        endpoint=endpoint,
        algorithm=algorithm,
        status=status
    ).inc()

    if not allowed:
        RATE_LIMIT_BLOCKS.labels(
            endpoint=endpoint,
            identifier_type=identifier_type
        ).inc()

    usage = count / limit if limit > 0 else 0
    RATE_LIMIT_USAGE.labels(endpoint=endpoint).set(usage)

    # Slack alert when usage > threshold
    if usage >= settings.ALERT_THRESHOLD and settings.SLACK_WEBHOOK_URL:
        await send_slack_alert(endpoint, usage, count, limit)

async def send_slack_alert(
    endpoint: str, usage: float, count: int, limit: int
):
    pct = int(usage * 100)
    msg = {
        "text": (
            f":warning: *Rate Limit Warning*\n"
            f"Endpoint `{endpoint}` is at *{pct}% capacity* "
            f"({count}/{limit} requests)."
        )
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.SLACK_WEBHOOK_URL, json=msg)
    except Exception:
        pass