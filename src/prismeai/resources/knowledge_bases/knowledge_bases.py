from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
from .documents import KBDocuments, AsyncKBDocuments
from .access import KBAccess, AsyncKBAccess
from .web_sources import KBWebSources, AsyncKBWebSources
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class KnowledgeBases:
    documents: KBDocuments
    access: KBAccess
    web_sources: KBWebSources
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.documents = KBDocuments(client, workspace_id)
        self.access = KBAccess(client, workspace_id)
        self.web_sources = KBWebSources(client, workspace_id)
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("knowledge_bases"), page_size=limit or 20, start_page=page or 1)
    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases"), json=kwargs)
    def get(self, knowledge_base_id: str) -> Any:
        return self._client.get(self._path("knowledge_bases", knowledge_base_id))
    def update(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("knowledge_bases", knowledge_base_id), json=kwargs)
    def delete(self, knowledge_base_id: str) -> None:
        self._client.delete(self._path("knowledge_bases", knowledge_base_id))
    def search(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "search"), json=kwargs)
    def reindex(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "reindex"), json=kwargs)

class AsyncKnowledgeBases:
    documents: AsyncKBDocuments
    access: AsyncKBAccess
    web_sources: AsyncKBWebSources
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.documents = AsyncKBDocuments(client, workspace_id)
        self.access = AsyncKBAccess(client, workspace_id)
        self.web_sources = AsyncKBWebSources(client, workspace_id)
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("knowledge_bases"), page_size=limit or 20, start_page=page or 1)
    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases"), json=kwargs)
    async def get(self, knowledge_base_id: str) -> Any:
        return await self._client.get(self._path("knowledge_bases", knowledge_base_id))
    async def update(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("knowledge_bases", knowledge_base_id), json=kwargs)
    async def delete(self, knowledge_base_id: str) -> None:
        await self._client.delete(self._path("knowledge_bases", knowledge_base_id))
    async def search(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "search"), json=kwargs)
    async def reindex(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "reindex"), json=kwargs)
