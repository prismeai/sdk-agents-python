from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Analytics:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def get(self, agent_id: str, *, period: Optional[str] = None, granularity: Optional[str] = None) -> Any:
        params: dict[str, Any] = {}
        if period: params["period"] = period
        if granularity: params["granularity"] = granularity
        return self._client.get(self._path("agents", agent_id, "analytics"), params=params)

class AsyncAnalytics:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    async def get(self, agent_id: str, *, period: Optional[str] = None, granularity: Optional[str] = None) -> Any:
        params: dict[str, Any] = {}
        if period: params["period"] = period
        if granularity: params["granularity"] = granularity
        return await self._client.get(self._path("agents", agent_id, "analytics"), params=params)
