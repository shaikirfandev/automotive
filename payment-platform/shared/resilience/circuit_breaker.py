"""Circuit breaker implementation for fault tolerance.

States:
  CLOSED: Normal operation. Failures are counted.
  OPEN: Requests fail immediately. No calls to downstream.
  HALF_OPEN: Limited requests pass through to test recovery.

Why circuit breakers?
  Without them, a failing downstream service causes:
  - Thread/connection pool exhaustion
  - Cascading failures across services
  - Increased latency for all users
  - Resource starvation

  With circuit breaker:
  - Fast failure when downstream is unhealthy
  - Automatic recovery detection
  - Resource protection
"""
import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypeVar
from functools import wraps

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Async circuit breaker implementation.
    
    Args:
        failure_threshold: Number of failures before opening circuit.
        recovery_timeout: Seconds to wait before attempting recovery.
        half_open_max_calls: Max calls allowed in half-open state.
        excluded_exceptions: Exceptions that don't count as failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
        excluded_exceptions: tuple[type[Exception], ...] = (),
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._excluded_exceptions = excluded_exceptions
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, with automatic transition from OPEN to HALF_OPEN."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def _record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
        else:
            self._failure_count = 0

    def _record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
        elif self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection."""
        current_state = self.state
        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpen(f"Circuit is OPEN. Recovery in {self._recovery_timeout}s")

        if current_state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls > self._half_open_max_calls:
                raise CircuitBreakerOpen("Circuit is HALF_OPEN, max calls reached")

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except self._excluded_exceptions:
            self._record_success()
            raise
        except Exception:
            self._record_failure()
            raise

    def __call__(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Use as a decorator."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await self.call(func, *args, **kwargs)
        return wrapper
