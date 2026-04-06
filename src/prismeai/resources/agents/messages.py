from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from ..._streaming import Stream, AsyncStream

if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient


class Messages:
    """Agent messages resource (sync)."""

    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/{self._workspace_id}/webhooks/{parts}"

    def send(self, agent_id: str, **kwargs: Any) -> Any:
        """Send a message and get a complete response."""
        return self._client.post(
            self._path("agents", agent_id, "messages"),
            json=kwargs,
        )

    def stream(self, agent_id: str, **kwargs: Any) -> Stream[Any]:
        """Send a message and receive an SSE stream."""
        response = self._client.request(
            "POST",
            self._path("agents", agent_id, "messages", "stream"),
            json=kwargs,
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        return Stream(response)


class AsyncMessages:
    """Agent messages resource (async)."""

    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/{self._workspace_id}/webhooks/{parts}"

    async def send(self, agent_id: str, **kwargs: Any) -> Any:
        """Send a message and get a complete response."""
        return await self._client.post(
            self._path("agents", agent_id, "messages"),
            json=kwargs,
        )

    async def stream(self, agent_id: str, **kwargs: Any) -> AsyncStream[Any]:
        """Send a message and receive an SSE stream."""
        response = await self._client.request(
            "POST",
            self._path("agents", agent_id, "messages", "stream"),
            json=kwargs,
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        return AsyncStream(response)
