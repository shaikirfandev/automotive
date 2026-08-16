"""Distributed rate limiter using Redis sliding window."""
from typing import Any
import time


class RateLimiter:
    """Token bucket rate limiter with Redis backend.
    
    Uses sliding window log algorithm for precise rate limiting.
    
    Args:
        redis_client: Async Redis client
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
    """

    def __init__(self, redis_client: Any, max_requests: int = 100, window_seconds: int = 60):
        self._redis = redis_client
        self._max_requests = max_requests
        self._window_seconds = window_seconds

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        window_start = now - self._window_seconds
        pipe_key = f"rate_limit:{key}"

        pipe = self._redis.pipeline()
        # Remove old entries outside window
        pipe.zremrangebyscore(pipe_key, 0, window_start)
        # Count current entries
        pipe.zcard(pipe_key)
        # Add current request
        pipe.zadd(pipe_key, {str(now): now})
        # Set TTL
        pipe.expire(pipe_key, self._window_seconds)
        results = await pipe.execute()

        current_count = results[1]
        return current_count < self._max_requests

    async def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - self._window_seconds
        pipe_key = f"rate_limit:{key}"

        await self._redis.zremrangebyscore(pipe_key, 0, window_start)
        count = await self._redis.zcard(pipe_key)
        return max(0, self._max_requests - count)
