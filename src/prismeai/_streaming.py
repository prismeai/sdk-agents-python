from __future__ import annotations

import json
from typing import Any, Iterator, AsyncIterator, Generic, TypeVar, Optional

import httpx

T = TypeVar("T")


class Stream(Generic[T]):
    """Synchronous SSE stream. Use as context manager + iterator.

    Usage:
        with client.agents.messages.stream(agent_id, params) as stream:
            for event in stream:
                print(event)
    """

    _response: httpx.Response
    _decoder: SSEDecoder

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self._decoder = SSEDecoder()

    def __enter__(self) -> "Stream[T]":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        self._response.close()

    def __iter__(self) -> Iterator[T]:
        for line in self._response.iter_lines():
            events = self._decoder.feed(line)
            for event in events:
                if event is not None:
                    yield event  # type: ignore[misc]


class AsyncStream(Generic[T]):
    """Asynchronous SSE stream. Use as async context manager + async iterator.

    Usage:
        async with client.agents.messages.stream(agent_id, params) as stream:
            async for event in stream:
                print(event)
    """

    _response: httpx.Response
    _decoder: SSEDecoder

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self._decoder = SSEDecoder()

    async def __aenter__(self) -> "AsyncStream[T]":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._response.aclose()

    async def __aiter__(self) -> AsyncIterator[T]:
        async for line in self._response.aiter_lines():
            events = self._decoder.feed(line)
            for event in events:
                if event is not None:
                    yield event  # type: ignore[misc]


class SSEDecoder:
    """Parse SSE protocol lines into events."""

    _data: list[str]
    _event_type: str

    def __init__(self) -> None:
        self._data = []
        self._event_type = ""

    def feed(self, line: str) -> list[Optional[Any]]:
        """Feed a single line. Returns list of parsed events (may be empty)."""
        results: list[Optional[Any]] = []

        if not line:
            # Empty line = end of event block
            if self._data:
                event = self._dispatch()
                if event is not None:
                    results.append(event)
            return results

        if line.startswith("data:"):
            value = line[5:].lstrip()
            self._data.append(value)
        elif line.startswith("event:"):
            self._event_type = line[6:].lstrip()
        # Ignore id:, retry:, and comments (:)

        return results

    def _dispatch(self) -> Optional[Any]:
        data = "\n".join(self._data)
        event_type = self._event_type

        # Reset state
        self._data = []
        self._event_type = ""

        if not data or data == "[DONE]":
            return None

        try:
            parsed = json.loads(data)
            if event_type:
                parsed["__event"] = event_type
            return parsed
        except (json.JSONDecodeError, TypeError):
            return {"data": data, "event": event_type or None}
