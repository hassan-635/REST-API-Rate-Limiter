from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    #jwt
    SECRET_KEY: str = "this_is_dummy_secret_key"
    ALGORITHM: str = "HS256"

    #global rate limit 
    GLOBAL_RATE_LIMIT: int = 10000
    GLOBAL_WINDOW: int = 60 #per minute

    #whitelist/blacklist
    WHITELISTED_IPS: List[str] = ["127.0.0.1", "::1"]
    BLACKLISTED_IPS: List[str] = []

    #monitoring
    SLACK_WEBHOOK_URL: str = ""
    ALERT_THRESHOLD: float = 0.80 # 80% usage triggers alert

    class Config:
        env_file = ".env"

settings = Settings()