from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class KBAccess:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, knowledge_base_id: str) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "access"))
    def grant(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "access"), json=kwargs)
    def update(self, knowledge_base_id: str, principal_type: str, principal_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("knowledge_bases", knowledge_base_id, "access", principal_type, principal_id), json=kwargs)
    def revoke(self, knowledge_base_id: str, principal_type: str, principal_id: str) -> None:
        self._client.delete(self._path("knowledge_bases", knowledge_base_id, "access", principal_type, principal_id))

class AsyncKBAccess:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, knowledge_base_id: str) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "access"))
    async def grant(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "access"), json=kwargs)
    async def update(self, knowledge_base_id: str, principal_type: str, principal_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("knowledge_bases", knowledge_base_id, "access", principal_type, principal_id), json=kwargs)
    async def revoke(self, knowledge_base_id: str, principal_type: str, principal_id: str) -> None:
        await self._client.delete(self._path("knowledge_bases", knowledge_base_id, "access", principal_type, principal_id))
