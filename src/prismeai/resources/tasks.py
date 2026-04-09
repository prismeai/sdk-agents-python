from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Tasks:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None, status: Optional[str] = None) -> SyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if status: params["status"] = status
        return SyncCursorPage(self._client, "GET", self._path("agents", agent_id, "tasks"), params=params, page_size=limit or 20, start_page=page or 1)
    def get(self, agent_id: str, task_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "tasks", task_id))
    def cancel(self, agent_id: str, task_id: str) -> Any:
        return self._client.post(self._path("agents", agent_id, "tasks", task_id, "cancel"))
    def subscribe(self, agent_id: str, task_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "tasks", task_id, "subscribe"))
    def resolve(self, agent_id: str, task_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents", agent_id, "tasks", task_id, "resolve"), json=kwargs)

class AsyncTasks:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None, status: Optional[str] = None) -> AsyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if status: params["status"] = status
        return AsyncCursorPage(self._client, "GET", self._path("agents", agent_id, "tasks"), params=params, page_size=limit or 20, start_page=page or 1)
    async def get(self, agent_id: str, task_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "tasks", task_id))
    async def cancel(self, agent_id: str, task_id: str) -> Any:
        return await self._client.post(self._path("agents", agent_id, "tasks", task_id, "cancel"))
    async def subscribe(self, agent_id: str, task_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "tasks", task_id, "subscribe"))
    async def resolve(self, agent_id: str, task_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents", agent_id, "tasks", task_id, "resolve"), json=kwargs)
