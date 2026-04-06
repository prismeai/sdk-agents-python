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
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, agent_id: Optional[str] = None, status: Optional[str] = None) -> SyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if agent_id: params["agentId"] = agent_id
        if status: params["status"] = status
        return SyncCursorPage(self._client, "GET", self._path("tasks"), params=params, page_size=limit or 20, start_page=page or 1)
    def get(self, task_id: str) -> Any:
        return self._client.get(self._path("tasks", task_id))
    def cancel(self, task_id: str) -> Any:
        return self._client.post(self._path("tasks", task_id, "cancel"))

class AsyncTasks:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, agent_id: Optional[str] = None, status: Optional[str] = None) -> AsyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if agent_id: params["agentId"] = agent_id
        if status: params["status"] = status
        return AsyncCursorPage(self._client, "GET", self._path("tasks"), params=params, page_size=limit or 20, start_page=page or 1)
    async def get(self, task_id: str) -> Any:
        return await self._client.get(self._path("tasks", task_id))
    async def cancel(self, task_id: str) -> Any:
        return await self._client.post(self._path("tasks", task_id, "cancel"))
