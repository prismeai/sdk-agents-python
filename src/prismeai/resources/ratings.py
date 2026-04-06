from __future__ import annotations
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Ratings:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    def create(self, **kwargs: Any) -> Any:
        return self._client.post(self._path("ratings"), json=kwargs)

class AsyncRatings:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return f"/workspaces/{self._workspace_id}/webhooks/{'/'.join(segments)}"
    async def create(self, **kwargs: Any) -> Any:
        return await self._client.post(self._path("ratings"), json=kwargs)
