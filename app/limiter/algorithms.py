import time
import redis.asyncio as aioredis
from dataclasses import dataclass

@dataclass
class LimitResult:
    allowed: bool
    count: int
    limit: int
    remaining: int
    reset_at: int          # unix timestamp
    retry_after: int       # seconds


async def fixed_window(
    r: aioredis.Redis,
    key: str,
    limit: int,
    window: int,
) -> LimitResult:

    pipe = r.pipeline()
    pipe.incr(key)
    pipe.ttl(key)
    count, ttl = await pipe.execute()

    if count == 1:
        await r.expire(key, window)
        ttl = window

    reset_at   = int(time.time()) + max(ttl, 0)
    remaining  = max(0, limit - count)
    allowed    = count <= limit

    return LimitResult(
        allowed=allowed, count=count, limit=limit,
        remaining=remaining, reset_at=reset_at,
        retry_after=max(ttl, 0) if not allowed else 0,
    )


async def sliding_window(
    r: aioredis.Redis,
    key: str,
    limit: int,
    window: int,
) -> LimitResult:
    now     = time.time()
    cutoff  = now - window
    now_ms  = str(now)          # score = float timestamp

    pipe = r.pipeline()
    pipe.zadd(key, {now_ms: now})
    pipe.zremrangebyscore(key, "-inf", cutoff)
    pipe.zcard(key)
    pipe.expire(key, window + 1)
    _, _, count, _ = await pipe.execute()

    reset_at  = int(now) + window
    remaining = max(0, limit - count)
    allowed   = count <= limit

    return LimitResult(
        allowed=allowed, count=count, limit=limit,
        remaining=remaining, reset_at=reset_at,
        retry_after=int(window) if not allowed else 0,
    )


# Lua script: atomic token bucket in Redis
_TOKEN_BUCKET_SCRIPT = """
local key       = KEYS[1]
local capacity  = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])   -- tokens per second
local now       = tonumber(ARGV[3])
local cost      = tonumber(ARGV[4])     -- tokens per request

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens     = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
local refilled = elapsed * refill_rate
tokens = math.min(capacity, tokens + refilled)

local allowed = 0
if tokens >= cost then
    tokens  = tokens - cost
    allowed = 1
end

redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)

return { allowed, math.floor(tokens), math.floor(capacity) }
"""

async def token_bucket(
    r: aioredis.Redis,
    key: str,
    capacity: int,     # max tokens (= burst limit)
    refill_rate: float,  # tokens refilled per second
    cost: int = 1,     # tokens consumed per request
) -> LimitResult:
    """
    Lua script ensures atomic read-modify-write.
    Supports burst traffic up to `capacity` then smooths.
    """
    now     = time.time()
    result  = await r.eval(
        _TOKEN_BUCKET_SCRIPT, 1, key,
        capacity, refill_rate, now, cost
    )
    allowed_int, tokens, cap = result
    allowed   = bool(allowed_int)
    remaining = int(tokens)

    # Time to refill 1 token
    retry_after = int((cost - tokens) / refill_rate) if not allowed else 0
    reset_at    = int(now) + int(cap / refill_rate)

    return LimitResult(
        allowed=allowed, count=cap - remaining, limit=cap,
        remaining=remaining, reset_at=reset_at,
        retry_after=max(retry_after, 1) if not allowed else 0,
    )
