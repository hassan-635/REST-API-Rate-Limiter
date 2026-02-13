
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from app.config import settings

async def require_admin(authorization: str = Header(...)):
    """Simple admin auth — extend with DB lookup in production."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Unauthorized")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(403, "Forbidden")
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid token")