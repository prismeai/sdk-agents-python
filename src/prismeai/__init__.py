"""Official Prisme.ai Python SDK for Agent Factory and Storage APIs."""

from .client import PrismeAI
from .async_client import AsyncPrismeAI
from ._version import __version__
from .resources.agents.messages import FileAttachment
from ._exceptions import (
    PrismeAIError,
    APIStatusError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    ValidationError,
    RateLimitError,
    InternalServerError,
    ConnectionError,
    TimeoutError,
)

__all__ = [
    "PrismeAI",
    "AsyncPrismeAI",
    "__version__",
    "PrismeAIError",
    "APIStatusError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "InternalServerError",
    "ConnectionError",
    "TimeoutError",
    "FileAttachment",
]
