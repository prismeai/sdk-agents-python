from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
from .vs_files import VSFiles, AsyncVSFiles
from .vs_access import VSAccess, AsyncVSAccess
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class VectorStores:
    files: VSFiles
    access: VSAccess
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.files = VSFiles(client, workspace_id)
        self.access = VSAccess(client, workspace_id)
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("vector_stores"), page_size=limit or 20, start_page=page or 1)
    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("vector_stores"), json=kwargs)
    def get(self, vector_store_id: str) -> Any:
        return self._client.get(self._path("vector_stores", vector_store_id))
    def update(self, vector_store_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("vector_stores", vector_store_id), json=kwargs)
    def delete(self, vector_store_id: str) -> None:
        self._client.delete(self._path("vector_stores", vector_store_id))
    def search(self, vector_store_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("vector_stores", vector_store_id, "search"), json=kwargs)
    def reindex(self, vector_store_id: str) -> None:
        self._client.post(self._path("vector_stores", vector_store_id, "reindex"))
    def crawl_status(self, vector_store_id: str) -> Any:
        return self._client.get(self._path("vector_stores", vector_store_id, "crawl_status"))
    def recrawl(self, vector_store_id: str) -> None:
        self._client.post(self._path("vector_stores", vector_store_id, "recrawl"))

class AsyncVectorStores:
    files: AsyncVSFiles
    access: AsyncVSAccess
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.files = AsyncVSFiles(client, workspace_id)
        self.access = AsyncVSAccess(client, workspace_id)
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("vector_stores"), page_size=limit or 20, start_page=page or 1)
    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("vector_stores"), json=kwargs)
    async def get(self, vector_store_id: str) -> Any:
        return await self._client.get(self._path("vector_stores", vector_store_id))
    async def update(self, vector_store_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("vector_stores", vector_store_id), json=kwargs)
    async def delete(self, vector_store_id: str) -> None:
        await self._client.delete(self._path("vector_stores", vector_store_id))
    async def search(self, vector_store_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("vector_stores", vector_store_id, "search"), json=kwargs)
    async def reindex(self, vector_store_id: str) -> None:
        await self._client.post(self._path("vector_stores", vector_store_id, "reindex"))
    async def crawl_status(self, vector_store_id: str) -> Any:
        return await self._client.get(self._path("vector_stores", vector_store_id, "crawl_status"))
    async def recrawl(self, vector_store_id: str) -> None:
        await self._client.post(self._path("vector_stores", vector_store_id, "recrawl"))
