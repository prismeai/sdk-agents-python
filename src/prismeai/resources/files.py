from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from .._pagination import SyncCursorPage, AsyncCursorPage
from .._files import FileInput, prepare_file
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient

class Files:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        return SyncCursorPage(self._client, "GET", self._path("files"), page_size=limit or 20, start_page=page or 1)
    def upload(self, file: FileInput, *, filename: Optional[str] = None, content_type: Optional[str] = None) -> Any:
        files = prepare_file("file", file, filename=filename, content_type=content_type)
        return self._client.post(self._path("files"), files=files)
    def get(self, file_id: str) -> Any:
        return self._client.get(self._path("files", file_id))
    def delete(self, file_id: str) -> None:
        self._client.delete(self._path("files", file_id))
    def download(self, file_id: str) -> Any:
        return self._client.request("GET", self._path("files", file_id, "content"), raw=True)

class AsyncFiles:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"
    def list(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        return AsyncCursorPage(self._client, "GET", self._path("files"), page_size=limit or 20, start_page=page or 1)
    async def upload(self, file: FileInput, *, filename: Optional[str] = None, content_type: Optional[str] = None) -> Any:
        files = prepare_file("file", file, filename=filename, content_type=content_type)
        return await self._client.post(self._path("files"), files=files)
    async def get(self, file_id: str) -> Any:
        return await self._client.get(self._path("files", file_id))
    async def delete(self, file_id: str) -> None:
        await self._client.delete(self._path("files", file_id))
    async def download(self, file_id: str) -> Any:
        return await self._client.request("GET", self._path("files", file_id, "content"), raw=True)
