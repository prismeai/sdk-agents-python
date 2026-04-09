from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Evaluations:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("agents", agent_id, "evaluations"), page_size=limit or 20, start_page=page or 1)
    def create(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents", agent_id, "evaluations"), json=kwargs)

class AsyncEvaluations:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("agents", agent_id, "evaluations"), page_size=limit or 20, start_page=page or 1)
    async def create(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents", agent_id, "evaluations"), json=kwargs)
