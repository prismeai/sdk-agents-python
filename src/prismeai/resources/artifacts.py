from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Artifacts:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("artifacts"), page_size=limit or 20, start_page=page or 1)
    def get(self, artifact_id: str) -> Any:
        return self._client.get(self._path("artifacts", artifact_id))
    def update(self, artifact_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("artifacts", artifact_id), json=kwargs)
    def delete(self, artifact_id: str) -> None:
        self._client.delete(self._path("artifacts", artifact_id))
    def share(self, artifact_id: str, **kwargs: Any) -> None:
        self._client.post(self._path("artifacts", artifact_id, "share"), json=kwargs)

class AsyncArtifacts:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("artifacts"), page_size=limit or 20, start_page=page or 1)
    async def get(self, artifact_id: str) -> Any:
        return await self._client.get(self._path("artifacts", artifact_id))
    async def update(self, artifact_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("artifacts", artifact_id), json=kwargs)
    async def delete(self, artifact_id: str) -> None:
        await self._client.delete(self._path("artifacts", artifact_id))
    async def share(self, artifact_id: str, **kwargs: Any) -> None:
        await self._client.post(self._path("artifacts", artifact_id, "share"), json=kwargs)
