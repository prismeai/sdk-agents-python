from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Profiles:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, search: Optional[str] = None) -> SyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if search:
            params["search"] = search
        return SyncCursorPage(self._client, "GET", self._path("profiles"), params=params, page_size=limit or 20, start_page=page or 1)

class AsyncProfiles:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None, search: Optional[str] = None) -> AsyncCursorPage[Any]:
        params: dict[str, Any] = {}
        if search:
            params["search"] = search
        return AsyncCursorPage(self._client, "GET", self._path("profiles"), params=params, page_size=limit or 20, start_page=page or 1)
