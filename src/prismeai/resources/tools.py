from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Tools:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("tools"), page_size=limit or 20, start_page=page or 1)
    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("tools"), json=kwargs)
    def get(self, tool_id: str) -> Any:
        return self._client.get(self._path("tools", tool_id))

class AsyncTools:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("tools"), page_size=limit or 20, start_page=page or 1)
    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("tools"), json=kwargs)
    async def get(self, tool_id: str) -> Any:
        return await self._client.get(self._path("tools", tool_id))
