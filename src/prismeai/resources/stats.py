from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Stats:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def get(self, *, period: Optional[str] = None) -> Any:
        params: dict[str, Any] = {}
        if period: params["period"] = period
        return self._client.get(self._path("stats"), params=params)

class AsyncStats:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    async def get(self, *, period: Optional[str] = None) -> Any:
        params: dict[str, Any] = {}
        if period: params["period"] = period
        return await self._client.get(self._path("stats"), params=params)
