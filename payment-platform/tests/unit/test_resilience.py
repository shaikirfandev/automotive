"""Unit tests for resilience patterns."""
import pytest
import asyncio
from shared.resilience.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpen
from services.payment_service.service import validate_transition
from services.payment_service.schemas import PaymentStatus


class TestCircuitBreaker:
    """Test circuit breaker state machine."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        async def failing_func():
            raise RuntimeError("Service down")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_immediately(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)

        async def failing_func():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            await cb.call(failing_func)

        with pytest.raises(CircuitBreakerOpen):
            await cb.call(failing_func)

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3)

        async def ok_func():
            return "ok"

        async def fail_func():
            raise RuntimeError("fail")

        # 2 failures
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(fail_func)

        # 1 success resets
        result = await cb.call(ok_func)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_excluded_exceptions_dont_count(self):
        cb = CircuitBreaker(
            failure_threshold=2,
            excluded_exceptions=(ValueError,),
        )

        async def raise_value_error():
            raise ValueError("not a failure")

        # ValueError should not count as failure
        for _ in range(5):
            with pytest.raises(ValueError):
                await cb.call(raise_value_error)

        assert cb.state == CircuitState.CLOSED
