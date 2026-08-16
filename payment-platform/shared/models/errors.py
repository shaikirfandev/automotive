"""Domain error definitions.

Standardized error hierarchy for consistent error handling across services.
Each error maps to a specific HTTP status code and error code.
"""


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message=message, code=code, status_code=404)


class ValidationError(AppError):
    """Validation failed."""

    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR"):
        super().__init__(message=message, code=code, status_code=422)


class DuplicateError(AppError):
    """Duplicate resource."""

    def __init__(self, message: str = "Resource already exists", code: str = "DUPLICATE"):
        super().__init__(message=message, code=code, status_code=409)


class InsufficientBalanceError(AppError):
    """Insufficient balance for operation."""

    def __init__(self, message: str = "Insufficient balance", code: str = "INSUFFICIENT_BALANCE"):
        super().__init__(message=message, code=code, status_code=400)


class UnauthorizedError(AppError):
    """Authentication/authorization failure."""

    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(message=message, code=code, status_code=401)


class RateLimitError(AppError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(message=message, code=code, status_code=429)


class ServiceUnavailableError(AppError):
    """External service unavailable."""

    def __init__(self, message: str = "Service unavailable", code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(message=message, code=code, status_code=503)
