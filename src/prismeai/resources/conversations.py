from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .._pagination import SyncCursorPage, AsyncCursorPage

if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient


class _BaseMixin:
    _workspace_id: str

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"


class Conversations(_BaseMixin):
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("agents", agent_id, "conversations"), page_size=limit or 20, start_page=page or 1)

    def create(self, agent_id: str, **kwargs: Any) -> Any:
        result = self._client.post(self._path("agents", agent_id, "conversations"), json=kwargs)
        # API returns contextId — normalize to id
        if isinstance(result, dict) and not result.get("id") and result.get("contextId"):
            result["id"] = result["contextId"]
        return result

    def get(self, agent_id: str, conversation_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "conversations", conversation_id))

    def update(self, agent_id: str, conversation_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("agents", agent_id, "conversations", conversation_id), json=kwargs)

    def delete(self, agent_id: str, conversation_id: str) -> None:
        self._client.delete(self._path("agents", agent_id, "conversations", conversation_id))

    def share(self, agent_id: str, conversation_id: str, **kwargs: Any) -> None:
        self._client.post(self._path("agents", agent_id, "conversations", conversation_id, "share"), json=kwargs)


class AsyncConversations(_BaseMixin):
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def list(self, agent_id: str, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("agents", agent_id, "conversations"), page_size=limit or 20, start_page=page or 1)

    async def create(self, agent_id: str, **kwargs: Any) -> Any:
        result = await self._client.post(self._path("agents", agent_id, "conversations"), json=kwargs)
        # API returns contextId — normalize to id
        if isinstance(result, dict) and not result.get("id") and result.get("contextId"):
            result["id"] = result["contextId"]
        return result

    async def get(self, agent_id: str, conversation_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "conversations", conversation_id))

    async def update(self, agent_id: str, conversation_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("agents", agent_id, "conversations", conversation_id), json=kwargs)

    async def delete(self, agent_id: str, conversation_id: str) -> None:
        await self._client.delete(self._path("agents", agent_id, "conversations", conversation_id))

    async def share(self, agent_id: str, conversation_id: str, **kwargs: Any) -> None:
        await self._client.post(self._path("agents", agent_id, "conversations", conversation_id, "share"), json=kwargs)
