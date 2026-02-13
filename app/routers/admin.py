
from fastapi import APIRouter, Depends, HTTPException
from app.utils.redis_client import get_redis
from app.dependencies import require_admin
import redis.asyncio as aioredis
import time

router = APIRouter(prefix="/admin/ratelimit", tags=["Admin - Rate Limit"])

@router.get("/{ip}", summary="Check IP rate limit status")
async def get_ip_status(
    ip: str,
    r: aioredis.Redis = Depends(get_redis),
    _=Depends(require_admin),
):
    pattern  = f"*:{ip}:*"
    keys     = await r.keys(pattern)
    statuses = []

    for key in keys:
        key_type = await r.type(key)
        if key_type == "string":
            count = int(await r.get(key) or 0)
            ttl   = await r.ttl(key)
            statuses.append({
                "key": key, "type": "fixed_window",
                "count": count, "ttl": ttl
            })
        elif key_type == "zset":
            count = await r.zcard(key)
            ttl   = await r.ttl(key)
            statuses.append({
                "key": key, "type": "sliding_window",
                "count": count, "ttl": ttl
            })
        elif key_type == "hash":
            data = await r.hgetall(key)
            statuses.append({
                "key": key, "type": "token_bucket",
                "tokens": data.get("tokens"), "last_refill": data.get("last_refill")
            })

    return {"ip": ip, "keys_found": len(statuses), "statuses": statuses}


@router.post("/reset", summary="Reset rate limits for IP/user")
async def reset_limits(
    ip: str | None = None,
    user_id: str | None = None,
    r: aioredis.Redis = Depends(get_redis),
    _=Depends(require_admin),
):
    deleted = 0
    if ip:
        keys = await r.keys(f"*:{ip}:*")
        if keys:
            deleted += await r.delete(*keys)
    if user_id:
        keys = await r.keys(f"*:user:{user_id}:*")
        if keys:
            deleted += await r.delete(*keys)

    return {"message": f"Cleared {deleted} rate limit keys"}


@router.get("/stats/overview", summary="Overall rate limit statistics")
async def get_stats(
    r: aioredis.Redis = Depends(get_redis),
    _=Depends(require_admin),
):
    fixed_keys   = await r.keys("ratelimit:*")
    sliding_keys = await r.keys("sliding:*")
    bucket_keys  = await r.keys("tokenbucket:*")
    global_keys  = await r.keys("global:*")

    # Count total blocked (keys with count > limit is hard without context,
    # so we return raw counts as proxy metrics)
    return {
        "timestamp":           int(time.time()),
        "active_fixed_windows":   len(fixed_keys),
        "active_sliding_windows": len(sliding_keys),
        "active_token_buckets":   len(bucket_keys),
        "active_global_limits":   len(global_keys),
        "total_tracked_keys":     (
            len(fixed_keys) + len(sliding_keys) +
            len(bucket_keys) + len(global_keys)
        ),
    }