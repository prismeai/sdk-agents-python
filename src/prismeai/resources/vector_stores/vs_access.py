from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class VSAccess:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, vector_store_id: str) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("vector-stores", vector_store_id, "access"))
    def grant(self, vector_store_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("vector-stores", vector_store_id, "access"), json=kwargs)
    def update(self, vector_store_id: str, access_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("vector-stores", vector_store_id, "access", access_id), json=kwargs)
    def revoke(self, vector_store_id: str, access_id: str) -> None:
        self._client.delete(self._path("vector-stores", vector_store_id, "access", access_id))

class AsyncVSAccess:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def list(self, vector_store_id: str) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("vector-stores", vector_store_id, "access"))
    async def grant(self, vector_store_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("vector-stores", vector_store_id, "access"), json=kwargs)
    async def update(self, vector_store_id: str, access_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("vector-stores", vector_store_id, "access", access_id), json=kwargs)
    async def revoke(self, vector_store_id: str, access_id: str) -> None:
        await self._client.delete(self._path("vector-stores", vector_store_id, "access", access_id))
