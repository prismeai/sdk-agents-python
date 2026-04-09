from __future__ import annotations

from typing import Generic, TypeVar, Optional

import httpx

T = TypeVar("T")


class APIResponse(Generic[T]):
    """Wrapper around an HTTP response that holds the parsed result."""

    _parsed: Optional[T]
    http_response: httpx.Response

    def __init__(self, *, raw: httpx.Response, parsed: Optional[T] = None) -> None:
        self.http_response = raw
        self._parsed = parsed

    @property
    def status_code(self) -> int:
        return self.http_response.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self.http_response.headers

    @property
    def parsed(self) -> T:
        if self._parsed is None:
            raise ValueError("Response has not been parsed")
        return self._parsed
