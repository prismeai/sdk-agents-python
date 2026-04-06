from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .._pagination import SyncCursorPage, AsyncCursorPage

if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient


class _BaseMixin:
    _workspace_id: str

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/{self._workspace_id}/webhooks/{parts}"


class Conversations(_BaseMixin):
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, agent_id: Optional[str] = None) -> SyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if agent_id:
            params["agentId"] = agent_id
        return SyncCursorPage(self._client, "GET", self._path("conversations"), params=params, page_size=limit or 20, start_page=page or 1)

    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("conversations"), json=kwargs)

    def get(self, conversation_id: str) -> Any:
        return self._client.get(self._path("conversations", conversation_id))

    def update(self, conversation_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("conversations", conversation_id), json=kwargs)

    def delete(self, conversation_id: str) -> None:
        self._client.delete(self._path("conversations", conversation_id))

    def messages(self, conversation_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("conversations", conversation_id, "messages"), page_size=limit or 20, start_page=page or 1)

    def share(self, conversation_id: str, **kwargs: Any) -> None:
        self._client.post(self._path("conversations", conversation_id, "share"), json=kwargs)


class AsyncConversations(_BaseMixin):
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, agent_id: Optional[str] = None) -> AsyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if agent_id:
            params["agentId"] = agent_id
        return AsyncCursorPage(self._client, "GET", self._path("conversations"), params=params, page_size=limit or 20, start_page=page or 1)

    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("conversations"), json=kwargs)

    async def get(self, conversation_id: str) -> Any:
        return await self._client.get(self._path("conversations", conversation_id))

    async def update(self, conversation_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("conversations", conversation_id), json=kwargs)

    async def delete(self, conversation_id: str) -> None:
        await self._client.delete(self._path("conversations", conversation_id))

    def messages(self, conversation_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("conversations", conversation_id, "messages"), page_size=limit or 20, start_page=page or 1)

    async def share(self, conversation_id: str, **kwargs: Any) -> None:
        await self._client.post(self._path("conversations", conversation_id, "share"), json=kwargs)
