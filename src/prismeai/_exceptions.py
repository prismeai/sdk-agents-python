from __future__ import annotations

from typing import Any, Optional


class PrismeAIError(Exception):
    """Base exception for all Prisme.ai SDK errors."""

    message: str
    status_code: Optional[int]
    body: Any
    headers: Optional[dict[str, str]]

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        body: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body
        self.headers = headers


class APIStatusError(PrismeAIError):
    """Error raised when the API returns a non-2xx status code."""


class AuthenticationError(APIStatusError):
    """401 Unauthorized."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=401, **kwargs)


class PermissionDeniedError(APIStatusError):
    """403 Forbidden."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(APIStatusError):
    """404 Not Found."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=404, **kwargs)


class ConflictError(APIStatusError):
    """409 Conflict."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=409, **kwargs)


class ValidationError(APIStatusError):
    """422 Unprocessable Entity."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=422, **kwargs)


class RateLimitError(APIStatusError):
    """429 Too Many Requests."""

    retry_after: Optional[float]

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = _parse_retry_after(self.headers)


class InternalServerError(APIStatusError):
    """5xx Server Error."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=500, **kwargs)


class ConnectionError(PrismeAIError):
    """Network connection error."""


class TimeoutError(PrismeAIError):
    """Request timed out."""


def _parse_retry_after(headers: Optional[dict[str, str]]) -> Optional[float]:
    if not headers:
        return None
    value = headers.get("retry-after")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def error_from_status(
    status_code: int,
    message: str,
    body: Any = None,
    headers: Optional[dict[str, str]] = None,
) -> APIStatusError:
    kwargs = {"body": body, "headers": headers}
    if status_code == 401:
        return AuthenticationError(message, **kwargs)
    if status_code == 403:
        return PermissionDeniedError(message, **kwargs)
    if status_code == 404:
        return NotFoundError(message, **kwargs)
    if status_code == 409:
        return ConflictError(message, **kwargs)
    if status_code == 422:
        return ValidationError(message, **kwargs)
    if status_code == 429:
        return RateLimitError(message, **kwargs)
    if status_code >= 500:
        return InternalServerError(message, **kwargs)
    return APIStatusError(message, status_code=status_code, **kwargs)
