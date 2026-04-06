from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from ..._pagination import SyncCursorPage, AsyncCursorPage
from .messages import Messages, AsyncMessages

if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient


class Agents:
    """Agent Factory agents resource (sync)."""

    messages: Messages

    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.messages = Messages(client, workspace_id)

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/{self._workspace_id}/webhooks/{parts}" if parts else f"/workspaces/{self._workspace_id}/webhooks"

    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        labels: Optional[str] = None,
        search: Optional[str] = None,
    ) -> SyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if labels:
            params["labels"] = labels
        if search:
            params["search"] = search
        return SyncCursorPage(
            self._client,
            "GET",
            self._path("agents"),
            params=params,
            page_size=limit or 20,
            start_page=page or 1,
        )

    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("agents"), json=kwargs)

    def get(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id))

    def update(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("agents", agent_id), json=kwargs)

    def delete(self, agent_id: str) -> None:
        self._client.delete(self._path("agents", agent_id))

    def publish(self, agent_id: str) -> Any:
        return self._client.post(self._path("agents", agent_id, "publish"))

    def discard_draft(self, agent_id: str) -> Any:
        return self._client.post(self._path("agents", agent_id, "discard-draft"))

    def discovery(self, agent_id: str, **kwargs: Any) -> Any:
        return self._client.patch(self._path("agents", agent_id, "discovery"), json=kwargs)

    def export(self, agent_id: str) -> Any:
        return self._client.get(self._path("agents", agent_id, "export"))

    def import_(self, config: dict[str, Any]) -> Any:
        return self._client.post(self._path("agents", "import"), json=config)


class AsyncAgents:
    """Agent Factory agents resource (async)."""

    messages: AsyncMessages

    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self.messages = AsyncMessages(client, workspace_id)

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/{self._workspace_id}/webhooks/{parts}" if parts else f"/workspaces/{self._workspace_id}/webhooks"

    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        labels: Optional[str] = None,
        search: Optional[str] = None,
    ) -> AsyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if labels:
            params["labels"] = labels
        if search:
            params["search"] = search
        return AsyncCursorPage(
            self._client,
            "GET",
            self._path("agents"),
            params=params,
            page_size=limit or 20,
            start_page=page or 1,
        )

    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("agents"), json=kwargs)

    async def get(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id))

    async def update(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("agents", agent_id), json=kwargs)

    async def delete(self, agent_id: str) -> None:
        await self._client.delete(self._path("agents", agent_id))

    async def publish(self, agent_id: str) -> Any:
        return await self._client.post(self._path("agents", agent_id, "publish"))

    async def discard_draft(self, agent_id: str) -> Any:
        return await self._client.post(self._path("agents", agent_id, "discard-draft"))

    async def discovery(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._client.patch(self._path("agents", agent_id, "discovery"), json=kwargs)

    async def export(self, agent_id: str) -> Any:
        return await self._client.get(self._path("agents", agent_id, "export"))

    async def import_(self, config: dict[str, Any]) -> Any:
        return await self._client.post(self._path("agents", "import"), json=config)
