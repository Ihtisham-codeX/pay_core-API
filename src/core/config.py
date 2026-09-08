import os


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "3"))
REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "3"))

# Idempotency keys expire so Redis does not keep every request forever.
REDIS_IDEMPOTENCY_TTL_SECONDS = int(os.getenv("REDIS_IDEMPOTENCY_TTL_SECONDS", "86400"))

# Simple user-based limiter: max requests within a sliding fixed window.
REDIS_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("REDIS_RATE_LIMIT_MAX_REQUESTS", "60"))
REDIS_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("REDIS_RATE_LIMIT_WINDOW_SECONDS", "60"))

# Cache-aside TTL for non-financial reads (e.g. user profile).
REDIS_CACHE_TTL_SECONDS = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "300"))
