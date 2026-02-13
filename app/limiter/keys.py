import time
from fastapi import Request
from jose import jwt, JWTError
from app.config import settings


def get_window(window: int) -> int:
    return int(time.time())

def build_key(prefix:str, identifier:str, endpoint: str, window: int) -> str:
    bucket = get_window(window)
    return f"{prefix}:{identifier}:{endpoint}:{bucket}"

def build_sliding_key(identifier: str, endpoint: str) -> str:
    return f"sliding:{identifier}:{endpoint}"

def build_token_bucket_key(identifier: str, endpoint: str) -> str:
    return f"tokenbucket:{identifier}:{endpoint}"


async def extract_identifier(request: Request, by: str) -> str:
    if by == "ip":
        forwarded = request.headers.get("X-Forwarded-For")
        return forwarded.split(",")[0].strip() if forwarded \
            else request.client.host

    elif by == "user":
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
                return f"user:{payload.get('sub', 'unknown')}"
            except JWTError:
                pass
        return f"ip:{request.client.host}"  # fallback

    elif by == "api_key":
        key = request.headers.get("X-API-Key", "")
        return f"apikey:{key}" if key else f"ip:{request.client.host}"

    return request.client.host