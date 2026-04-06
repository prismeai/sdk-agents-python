from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class VSFiles:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, vector_store_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("vector-stores", vector_store_id, "files"), page_size=limit or 20, start_page=page or 1)
    def add(self, vector_store_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("vector-stores", vector_store_id, "files"), json=kwargs)
    def delete(self, vector_store_id: str, file_id: str) -> None:
        self._client.delete(self._path("vector-stores", vector_store_id, "files", file_id))
    def chunks(self, vector_store_id: str, file_id: str) -> Any:
        return self._client.get(self._path("vector-stores", vector_store_id, "files", file_id, "chunks"))
    def reindex(self, vector_store_id: str, file_id: str) -> None:
        self._client.post(self._path("vector-stores", vector_store_id, "files", file_id, "reindex"))

class AsyncVSFiles:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, vector_store_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("vector-stores", vector_store_id, "files"), page_size=limit or 20, start_page=page or 1)
    async def add(self, vector_store_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("vector-stores", vector_store_id, "files"), json=kwargs)
    async def delete(self, vector_store_id: str, file_id: str) -> None:
        await self._client.delete(self._path("vector-stores", vector_store_id, "files", file_id))
    async def chunks(self, vector_store_id: str, file_id: str) -> Any:
        return await self._client.get(self._path("vector-stores", vector_store_id, "files", file_id, "chunks"))
    async def reindex(self, vector_store_id: str, file_id: str) -> None:
        await self._client.post(self._path("vector-stores", vector_store_id, "files", file_id, "reindex"))
