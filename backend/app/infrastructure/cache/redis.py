"""
Redis cache client for Project Atlas.

This module provides async Redis connectivity using redis-py.
It manages the Redis connection lifecycle and exposes a shared client
instance for use throughout the application.

The client must be initialized during application startup and properly
closed during shutdown to ensure clean resource management.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse, urlunparse

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Manages the application's shared asynchronous Redis client.

    This class is responsible for:

    - Creating the Redis client.
    - Verifying connectivity during startup.
    - Providing access to the shared client.
    - Closing the client during application shutdown.

    The client is intentionally initialized explicitly rather than during
    module import to avoid side effects and to support FastAPI's lifespan
    management.
    """

    def __init__(self) -> None:
        """Initialize the Redis client manager."""
        self._client: Redis | None = None

    async def initialize(self) -> None:
        """
        Initialize and verify the Redis connection.

        Raises:
            RuntimeError:
                If the client has already been initialized.

            redis.exceptions.ConnectionError:
                If Redis cannot be reached.

            redis.exceptions.TimeoutError:
                If the connection attempt times out.
        """
        if self._client is not None:
            raise RuntimeError("Redis client has already been initialized.")

        logger.info(
            "Initializing Redis client.",
            extra={"redis_url": self._mask_url(settings.redis_url)},
        )

        try:
            client = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )

            # Verify connectivity immediately.
            await client.ping()

            self._client = client

            logger.info("Redis connection verified successfully.")

        except (RedisConnectionError, RedisTimeoutError):
            logger.exception(
                "Failed to establish Redis connection.",
                extra={"redis_url": self._mask_url(settings.redis_url)},
            )
            raise

        except Exception:
            logger.exception("Unexpected error while initializing Redis.")
            raise

    async def close(self) -> None:
        """
        Close the Redis client.

        This method is idempotent. Calling it multiple times is safe.
        """
        if self._client is None:
            return

        logger.info("Closing Redis client.")

        try:
            await self._client.close()
        finally:
            self._client = None

        logger.info("Redis client closed.")

    def get_client(self) -> Redis:
        """
        Return the initialized Redis client.

        Raises:
            RuntimeError:
                If initialize() has not yet been called.
        """
        if self._client is None:
            raise RuntimeError(
                "Redis client has not been initialized. "
                "Call initialize() before requesting the client."
            )

        return self._client

    @staticmethod
    def _mask_url(url: str) -> str:
        """
        Mask credentials before writing a Redis URL to logs.
        """
        parsed = urlparse(url)

        if parsed.password is None:
            return url

        netloc = (
            f"{parsed.username}:***@{parsed.hostname}:{parsed.port}"
        )

        return urlunparse(parsed._replace(netloc=netloc))


# Shared application-wide Redis client.
redis_client = RedisClient()