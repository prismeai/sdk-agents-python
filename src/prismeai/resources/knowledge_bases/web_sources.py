from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class KBWebSources:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, knowledge_base_id: str) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "web_sources"))
    def add(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "web_sources"), json=kwargs)
    def get(self, knowledge_base_id: str, web_source_id: str) -> Any:
        return self._client.get(self._path("knowledge_bases", knowledge_base_id, "web_sources", web_source_id))
    def delete(self, knowledge_base_id: str, web_source_id: str) -> None:
        self._client.delete(self._path("knowledge_bases", knowledge_base_id, "web_sources", web_source_id))

class AsyncKBWebSources:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, knowledge_base_id: str) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "web_sources"))
    async def add(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "web_sources"), json=kwargs)
    async def get(self, knowledge_base_id: str, web_source_id: str) -> Any:
        return await self._client.get(self._path("knowledge_bases", knowledge_base_id, "web_sources", web_source_id))
    async def delete(self, knowledge_base_id: str, web_source_id: str) -> None:
        await self._client.delete(self._path("knowledge_bases", knowledge_base_id, "web_sources", web_source_id))
