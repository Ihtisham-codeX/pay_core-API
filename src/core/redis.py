import logging

import redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from src.core.config import (
    REDIS_DB,
    REDIS_DECODE_RESPONSES,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_SOCKET_CONNECT_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
    REDIS_SSL,
)

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis_client():
    """Return a shared Redis client, or None if Redis cannot be reached.

    Business services must not create their own connections. They go through
    RedisService, which uses this module.
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD or None,
            ssl=REDIS_SSL,
            decode_responses=REDIS_DECODE_RESPONSES,
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
            retry=Retry(NoBackoff(), 1),
        )
        client.ping()
        _redis_client = client
        logger.info("Redis connected at %s:%s db=%s", REDIS_HOST, REDIS_PORT, REDIS_DB)
    except Exception as exc:
        logger.error("Redis connection failed: %s", exc)
        _redis_client = None

    return _redis_client


def ping_redis() -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except Exception:
        return False


def close_redis_client() -> None:
    global _redis_client
    if _redis_client is None:
        return
    try:
        _redis_client.close()
    except Exception:
        logger.debug("Redis close failed", exc_info=True)
    _redis_client = None
