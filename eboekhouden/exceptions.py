"""Custom exceptions for the e-Boekhouden SDK."""

from typing import Any


class EBoekhoudenError(Exception):
    """Base exception for all e-Boekhouden errors."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class AuthenticationError(EBoekhoudenError):
    """Raised when authentication fails."""

    pass


class SessionExpiredError(AuthenticationError):
    """Raised when the session token has expired."""

    pass


class APIError(EBoekhoudenError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: str | None = None,
        error_type: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)
        self.status_code = status_code
        self.error_type = error_type


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status_code=404, code=code, details=details)


class ValidationError(APIError):
    """Raised when request validation fails (400)."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        errors: dict[str, list[str]] | None = None,
    ):
        details = {"errors": errors} if errors else None
        super().__init__(
            message,
            status_code=400,
            code=code,
            error_type="validation",
            details=details,
        )
        self.errors = errors or {}


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None
    ):
        details = {"retry_after": retry_after} if retry_after is not None else None
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class SecurityError(APIError):
    """Raised for security-related errors (403)."""

    def __init__(
        self, message: str, code: str | None = None, security_type: int | None = None
    ):
        super().__init__(message, status_code=403, code=code, error_type="security")
        self.security_type = security_type
