import redis.asyncio as aioredis
from app.config import settings

_redis_pool: aioredis.Redis | None = None

async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.Redis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
            db = settings.REDIS_DB,
            password = settings.REDIS_PASSWORD,
            decode_responses = True,
            max_connections = 50,
        )

    return _redis_pool

async def close_redis():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None

        