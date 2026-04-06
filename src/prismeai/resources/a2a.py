from __future__ import annotations
from typing import Any, TYPE_CHECKING
from .._streaming import Stream, AsyncStream
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class A2A:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def send(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents", agent_id, "a2a", "send"), json=kwargs)
    def send_subscribe(self, agent_id: str, **kwargs: Any) -> Stream[Any]:
        response = self._client.request("POST", self._path("agents", agent_id, "a2a", "send-subscribe"), json=kwargs, headers={"accept": "text/event-stream"}, raw=True)
        return Stream(response)
    def get_card(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "a2a", "card"))
    def get_extended_card(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "a2a", "card", "extended"))

class AsyncA2A:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    async def send(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents", agent_id, "a2a", "send"), json=kwargs)
    async def send_subscribe(self, agent_id: str, **kwargs: Any) -> AsyncStream[Any]:
        response = await self._client.request("POST", self._path("agents", agent_id, "a2a", "send-subscribe"), json=kwargs, headers={"accept": "text/event-stream"}, raw=True)
        return AsyncStream(response)
    async def get_card(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "a2a", "card"))
    async def get_extended_card(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "a2a", "card", "extended"))
