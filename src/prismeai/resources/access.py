from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Access:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("agents", agent_id, "access"), page_size=limit or 20, start_page=page or 1)
    def grant(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents", agent_id, "access"), json=kwargs)
    def revoke(self, agent_id: str, access_id: str) -> None:
        self._client.delete(self._path("agents", agent_id, "access", access_id))
    def request_access(self, agent_id: str) -> Any:
        return self._client.post(self._path("agents", agent_id, "access-requests"))
    def list_requests(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("agents", agent_id, "access-requests"), page_size=limit or 20, start_page=page or 1)
    def handle_request(self, agent_id: str, request_id: str, action: str) -> Any:
        return self._client.post(self._path("agents", agent_id, "access-requests", request_id, action))

class AsyncAccess:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("agents", agent_id, "access"), page_size=limit or 20, start_page=page or 1)
    async def grant(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents", agent_id, "access"), json=kwargs)
    async def revoke(self, agent_id: str, access_id: str) -> None:
        await self._client.delete(self._path("agents", agent_id, "access", access_id))
    async def request_access(self, agent_id: str) -> Any:
        return await self._client.post(self._path("agents", agent_id, "access-requests"))
    def list_requests(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("agents", agent_id, "access-requests"), page_size=limit or 20, start_page=page or 1)
    async def handle_request(self, agent_id: str, request_id: str, action: str) -> Any:
        return await self._client.post(self._path("agents", agent_id, "access-requests", request_id, action))
