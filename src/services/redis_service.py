import json
import logging
import re

from src.core.config import (
    REDIS_CACHE_TTL_SECONDS,
    REDIS_IDEMPOTENCY_TTL_SECONDS,
    REDIS_RATE_LIMIT_MAX_REQUESTS,
    REDIS_RATE_LIMIT_WINDOW_SECONDS,
)
from src.core.redis import get_redis_client

logger = logging.getLogger(__name__)

IDEMPOTENCY_PENDING = "PENDING"
IDEMPOTENCY_COMPLETED = "COMPLETED"

# Atomic fixed-window counter: INCR and set TTL only on the first hit. lua script
_RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
  redis.call("EXPIRE", KEYS[1], ARGV[1])
end
return current
"""


class RedisUnavailableError(RuntimeError):
    """Raised when Redis is required for a write-side control (idempotency, rate limit)."""

# caller never directly ta;ks to redis.py
class RedisService:

    def __init__(self, client=None):

        if client is not None:
            self.client = client
        else:
            self.client = get_redis_client()

    def is_available(self) -> bool:
        if self.client is None:
            return False
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    def require_client(self):
        if self.client is None:
            raise RedisUnavailableError("Redis unavailable")
        return self.client

    @staticmethod

    # just to clean values so can be added in redis
    def _normalize_key_part(value) -> str:
        return re.sub(r"[^a-zA-Z0-9:._-]+", "-", str(value)).strip("-")

    # defining and cleaning all the keys we need
    def idempotency_key(self, user_id: int, idempotency_key: str) -> str:
        request_key = self._normalize_key_part(idempotency_key)
        return f"idempotency:user:{user_id}:{request_key}"

    def rate_limit_key(self, user_id: int) -> str:
        return f"rate_limit:user:{user_id}"

    def rate_limit_ip_key(self, ip_address: str) -> str:
        return f"rate_limit:ip:{self._normalize_key_part(ip_address)}"

    def cache_user_key(self, user_id: int) -> str:
        return f"cache:user:{user_id}"

    def cache_transactions_key(self, user_id: int) -> str:
        return f"cache:transactions:user:{user_id}"

    # defining general redis functions

    def get(self, key: str):
        try:
            # if client is available get()
            return self.require_client().get(key)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    def set(self, key: str, value, ex: int | None = None, nx: bool = False):
        try:
            # ex = expiration time in seconds
            # nx = set only if doesnt exists 
            return self.require_client().set(key, value, ex=ex, nx=nx)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    def delete(self, key: str):
        try:
            return self.require_client().delete(key)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    def exists(self, key: str) -> bool:
        try:
            return bool(self.require_client().exists(key))
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    def increment(self, key: str):
        try:
            return self.require_client().incr(key)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    def expire(self, key: str, seconds: int): # to tell Redis delete this key after X seconds
        try:
            return self.require_client().expire(key, seconds)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc

    # to reserve the request key 
    def claim_idempotency_key(
        self,
        key: str,
        ttl_seconds: int = REDIS_IDEMPOTENCY_TTL_SECONDS,
    ) -> bool:
        """Atomically claim a key with SET NX EX. True means this request may proceed."""
        return bool(self.set(key, IDEMPOTENCY_PENDING, ex=ttl_seconds, nx=True))
    
    #gives current status of this request
    def get_idempotency_record(self, key: str) -> dict | None:
        value = self.get(key)
        if value is None:
            return None
        if value == IDEMPOTENCY_PENDING:
            return {"status": IDEMPOTENCY_PENDING, "result": None}
        try:
            parsed = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {"status": IDEMPOTENCY_COMPLETED, "result": value}
        if isinstance(parsed, dict) and parsed.get("status") == IDEMPOTENCY_COMPLETED:
            return parsed
        return {"status": IDEMPOTENCY_COMPLETED, "result": parsed}

    def complete_idempotency(
        self,
        key: str,
        result,
        ttl_seconds: int = REDIS_IDEMPOTENCY_TTL_SECONDS,
    ) -> None:
        payload = json.dumps({"status": IDEMPOTENCY_COMPLETED, "result": result})
        self.set(key, payload, ex=ttl_seconds, nx=False)

    #if the operation fails, so remove the temporary PENDING reservation
    def release_idempotency_key(self, key: str) -> None:
        """Clear PENDING after a failed transfer so the client can retry."""
        try:
            self.delete(key)
        except RedisUnavailableError:
            logger.error("Could not release idempotency key %s after failure", key)

    def check_rate_limit(
        self,
        key: str,
        limit: int = REDIS_RATE_LIMIT_MAX_REQUESTS,
        window_seconds: int = REDIS_RATE_LIMIT_WINDOW_SECONDS,
    ) -> bool:
        """Return True if the request is allowed. If we cannot check the rate limit, don't allow the request"""
        client = self.require_client()
        try:
            # hasattr -> "Does this object have this thing?"
            if hasattr(client, "eval"):
                count = client.eval(_RATE_LIMIT_SCRIPT, 1, key, window_seconds)
            else:
                count = self.increment(key)
                if count == 1:
                    self.expire(key, window_seconds)
        except RedisUnavailableError:
            raise
        except Exception as exc:
            raise RedisUnavailableError("Redis unavailable") from exc
        return int(count) <= limit

    def cache_get(self, key: str):
        """Cache reads fail open: a Redis outage is treated as a miss."""
        try:
            return self.get(key)
        except RedisUnavailableError:
            logger.warning("Redis cache GET failed for %s; falling back to source", key)
            return None

    def cache_set(self, key: str, value: str, ttl_seconds: int = REDIS_CACHE_TTL_SECONDS) -> None:
        try:
            self.set(key, value, ex=ttl_seconds, nx=False)
        except RedisUnavailableError:
            logger.warning("Redis cache SET failed for %s; continuing without cache", key)

    def cache_invalidate(self, key: str) -> None:
        try:
            self.delete(key)
        except RedisUnavailableError:
            logger.warning("Redis cache DELETE failed for %s", key)
