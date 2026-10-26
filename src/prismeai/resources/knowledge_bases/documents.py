from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from ..._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient

class KBDocuments:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(
        self,
        knowledge_base_id: str,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        source_type: Optional[str] = None,
        origin: Optional[str] = None,
        web_source_id: Optional[str] = None,
        scope: Optional[str] = None,
        conversation_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        search: Optional[str] = None,
        updated_before: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SyncCursorPage[Any]:
        """List documents in a knowledge base. `status` takes one status or a comma-separated list,
        `updated_before` is a Unix timestamp in seconds, and `tags={"project": "x"}` or
        `metadata={...}` filter on document fields. The server ignores, without error, a key outside
        `[A-Za-z0-9_-]` (dots nest up to 4 levels) or a value containing `[` or `]`."""
        params: dict[str, Any] = {
            "status": status, "source_type": source_type, "origin": origin, "web_source_id": web_source_id,
            "scope": scope, "conversation_id": conversation_id, "owner_user_id": owner_user_id,
            "search": search, "updated_before": updated_before,
            **{f"tags.{key}": value for key, value in (tags or {}).items()},
            **{f"metadata.{key}": value for key, value in (metadata or {}).items()},
        }
        return SyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "documents"), params=params, page_size=limit or 20, start_page=page or 1)
    def add(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "documents"), json=kwargs)
    def get(self, knowledge_base_id: str, document_id: str) -> Any:
        return self._client.get(self._path("knowledge_bases", knowledge_base_id, "documents", document_id))
    def update(self, knowledge_base_id: str, document_id: str, **kwargs: Any) -> Any:
        """Update document tags, metadata, expiry or filename."""
        return self._client.patch(self._path("knowledge_bases", knowledge_base_id, "documents", document_id), json=kwargs)
    def delete(self, knowledge_base_id: str, document_id: str) -> Any:
        """Remove a document. Its uploaded file is deleted too when no other document uses it and the
        document's owner uploaded it: `file_purged` says whether it was."""
        return self._client.delete(self._path("knowledge_bases", knowledge_base_id, "documents", document_id))
    def chunks(self, knowledge_base_id: str, document_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "chunks"), page_size=limit or 20, start_page=page or 1)
    def source_url(self, knowledge_base_id: str, document_id: str) -> Any:
        """Resolve a link to the document's source; an uploaded file's link expires (`expires_at`), resolve again after."""
        return self._client.get(self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "source_url"))
    def reindex(self, knowledge_base_id: str, document_id: str, **kwargs: Any) -> Any:
        return self._client.post(self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "reindex"), json=kwargs)

class AsyncKBDocuments:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(
        self,
        knowledge_base_id: str,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        source_type: Optional[str] = None,
        origin: Optional[str] = None,
        web_source_id: Optional[str] = None,
        scope: Optional[str] = None,
        conversation_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        search: Optional[str] = None,
        updated_before: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> AsyncCursorPage[Any]:
        """List documents in a knowledge base. `status` takes one status or a comma-separated list,
        `updated_before` is a Unix timestamp in seconds, and `tags={"project": "x"}` or
        `metadata={...}` filter on document fields. The server ignores, without error, a key outside
        `[A-Za-z0-9_-]` (dots nest up to 4 levels) or a value containing `[` or `]`."""
        params: dict[str, Any] = {
            "status": status, "source_type": source_type, "origin": origin, "web_source_id": web_source_id,
            "scope": scope, "conversation_id": conversation_id, "owner_user_id": owner_user_id,
            "search": search, "updated_before": updated_before,
            **{f"tags.{key}": value for key, value in (tags or {}).items()},
            **{f"metadata.{key}": value for key, value in (metadata or {}).items()},
        }
        return AsyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "documents"), params=params, page_size=limit or 20, start_page=page or 1)
    async def add(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "documents"), json=kwargs)
    async def get(self, knowledge_base_id: str, document_id: str) -> Any:
        return await self._client.get(self._path("knowledge_bases", knowledge_base_id, "documents", document_id))
    async def update(self, knowledge_base_id: str, document_id: str, **kwargs: Any) -> Any:
        """Update document tags, metadata, expiry or filename."""
        return await self._client.patch(self._path("knowledge_bases", knowledge_base_id, "documents", document_id), json=kwargs)
    async def delete(self, knowledge_base_id: str, document_id: str) -> Any:
        """Remove a document. Its uploaded file is deleted too when no other document uses it and the
        document's owner uploaded it: `file_purged` says whether it was."""
        return await self._client.delete(self._path("knowledge_bases", knowledge_base_id, "documents", document_id))
    def chunks(self, knowledge_base_id: str, document_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "chunks"), page_size=limit or 20, start_page=page or 1)
    async def source_url(self, knowledge_base_id: str, document_id: str) -> Any:
        """Resolve a link to the document's source; an uploaded file's link expires (`expires_at`), resolve again after."""
        return await self._client.get(self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "source_url"))
    async def reindex(self, knowledge_base_id: str, document_id: str, **kwargs: Any) -> Any:
        return await self._client.post(self._path("knowledge_bases", knowledge_base_id, "documents", document_id, "reindex"), json=kwargs)
