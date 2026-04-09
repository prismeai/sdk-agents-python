from __future__ import annotations
from typing import Any, TYPE_CHECKING
from .._streaming import Stream, AsyncStream
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

_req_id = 0

def _next_id() -> str:
    global _req_id
    _req_id += 1
    return f"req-{_req_id}"

class A2A:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def send(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents", agent_id, "a2a"), json={
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": kwargs,
            "id": _next_id(),
        })
    def send_subscribe(self, agent_id: str, **kwargs: Any) -> Stream[Any]:
        response = self._client.request("POST", self._path("agents", agent_id, "a2a"), json={
            "jsonrpc": "2.0",
            "method": "tasks/sendSubscribe",
            "params": kwargs,
            "id": _next_id(),
        }, headers={"accept": "text/event-stream"}, raw=True)
        return Stream(response)
    def get_card(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, ".well-known", "agent.json"))
    def get_extended_card(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "extendedAgentCard"))

class AsyncA2A:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    async def send(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents", agent_id, "a2a"), json={
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": kwargs,
            "id": _next_id(),
        })
    async def send_subscribe(self, agent_id: str, **kwargs: Any) -> AsyncStream[Any]:
        response = await self._client.request("POST", self._path("agents", agent_id, "a2a"), json={
            "jsonrpc": "2.0",
            "method": "tasks/sendSubscribe",
            "params": kwargs,
            "id": _next_id(),
        }, headers={"accept": "text/event-stream"}, raw=True)
        return AsyncStream(response)
    async def get_card(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, ".well-known", "agent.json"))
    async def get_extended_card(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "extendedAgentCard"))
