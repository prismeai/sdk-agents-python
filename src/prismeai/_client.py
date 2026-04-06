from __future__ import annotations

import time
import math
import random
from typing import Any, Optional, TypeVar, Type, Union

import httpx

from ._constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
    RETRY_STATUS_CODES,
)
from ._exceptions import (
    PrismeAIError,
    ConnectionError as PrismeConnectionError,
    TimeoutError as PrismeTimeoutError,
    RateLimitError,
    error_from_status,
)

T = TypeVar("T")


def _extract_error_message(body: Any, fallback: str) -> str:
    if isinstance(body, dict):
        if isinstance(body.get("message"), str):
            return body["message"]
        if isinstance(body.get("error"), str):
            return body["error"]
        if isinstance(body.get("error"), dict):
            inner = body["error"]
            if isinstance(inner.get("message"), str):
                return inner["message"]
    return fallback


def _get_retry_delay(attempt: int, last_error: Optional[PrismeAIError] = None) -> float:
    if isinstance(last_error, RateLimitError) and last_error.retry_after:
        return min(last_error.retry_after, MAX_RETRY_DELAY)
    base = INITIAL_RETRY_DELAY * math.pow(2, attempt - 1)
    jitter = base * 0.2 * random.random()
    return min(base + jitter, MAX_RETRY_DELAY)


class SyncAPIClient:
    """Synchronous HTTP client backed by httpx.Client."""

    _client: httpx.Client
    _base_url: str
    _max_retries: int

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict[str, str],
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SyncAPIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        # Strip None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        last_error: Optional[PrismeAIError] = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _get_retry_delay(attempt, last_error)
                time.sleep(delay)

            try:
                if files:
                    response = self._client.request(
                        method, path, params=params, files=files, headers=headers,
                    )
                else:
                    response = self._client.request(
                        method, path, json=json, params=params, headers=headers,
                    )
            except httpx.TimeoutException as e:
                if attempt < self._max_retries:
                    last_error = PrismeTimeoutError(str(e))
                    continue
                raise PrismeTimeoutError(str(e)) from e
            except httpx.ConnectError as e:
                if attempt < self._max_retries:
                    last_error = PrismeConnectionError(str(e))
                    continue
                raise PrismeConnectionError(str(e)) from e

            if response.is_success:
                if raw:
                    return response
                if not response.content:
                    return None
                try:
                    return response.json()
                except Exception:
                    return response.text

            body = _safe_parse(response)
            message = _extract_error_message(body, response.reason_phrase or "Unknown error")
            resp_headers = dict(response.headers)
            error = error_from_status(response.status_code, message, body=body, headers=resp_headers)

            if response.status_code in RETRY_STATUS_CODES and attempt < self._max_retries:
                last_error = error
                continue

            raise error

        raise last_error or PrismeAIError("Request failed after retries")

    def get(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any = None, files: Optional[dict[str, Any]] = None) -> Any:
        return self.request("POST", path, json=json, files=files)

    def put(self, path: str, *, json: Any = None) -> Any:
        return self.request("PUT", path, json=json)

    def patch(self, path: str, *, json: Any = None) -> Any:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        return self.request("DELETE", path, params=params)


class AsyncAPIClient:
    """Asynchronous HTTP client backed by httpx.AsyncClient."""

    _client: httpx.AsyncClient
    _base_url: str
    _max_retries: int

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict[str, str],
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncAPIClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        import anyio

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        last_error: Optional[PrismeAIError] = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _get_retry_delay(attempt, last_error)
                await anyio.sleep(delay)

            try:
                if files:
                    response = await self._client.request(
                        method, path, params=params, files=files, headers=headers,
                    )
                else:
                    response = await self._client.request(
                        method, path, json=json, params=params, headers=headers,
                    )
            except httpx.TimeoutException as e:
                if attempt < self._max_retries:
                    last_error = PrismeTimeoutError(str(e))
                    continue
                raise PrismeTimeoutError(str(e)) from e
            except httpx.ConnectError as e:
                if attempt < self._max_retries:
                    last_error = PrismeConnectionError(str(e))
                    continue
                raise PrismeConnectionError(str(e)) from e

            if response.is_success:
                if raw:
                    return response
                if not response.content:
                    return None
                try:
                    return response.json()
                except Exception:
                    return response.text

            body = _safe_parse(response)
            message = _extract_error_message(body, response.reason_phrase or "Unknown error")
            resp_headers = dict(response.headers)
            error = error_from_status(response.status_code, message, body=body, headers=resp_headers)

            if response.status_code in RETRY_STATUS_CODES and attempt < self._max_retries:
                last_error = error
                continue

            raise error

        raise last_error or PrismeAIError("Request failed after retries")

    async def get(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None, files: Optional[dict[str, Any]] = None) -> Any:
        return await self.request("POST", path, json=json, files=files)

    async def put(self, path: str, *, json: Any = None) -> Any:
        return await self.request("PUT", path, json=json)

    async def patch(self, path: str, *, json: Any = None) -> Any:
        return await self.request("PATCH", path, json=json)

    async def delete(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        return await self.request("DELETE", path, params=params)


def _safe_parse(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:
        try:
            return response.text
        except Exception:
            return None
