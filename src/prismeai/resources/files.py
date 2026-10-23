from __future__ import annotations
import json
from typing import Any, Optional, TYPE_CHECKING
from urllib.parse import quote
from .._pagination import SyncCursorPage, AsyncCursorPage, PageResponse
from .._files import FileInput, prepare_file
if TYPE_CHECKING:
    from .._client import SyncAPIClient, AsyncAPIClient


def _upload_parts(file: FileInput, filename: Optional[str], content_type: Optional[str], metadata: Optional[dict[str, Any]]) -> dict[str, Any]:
    parts: dict[str, Any] = prepare_file("file", file, filename=filename, content_type=content_type)
    parts["public"] = (None, "false")
    if metadata is not None:
        parts["metadata"] = (None, json.dumps(metadata))
    return parts


def _list_extractor(body: Any) -> PageResponse[Any]:
    # The files API returns a bare array: page fullness alone decides whether a next page exists.
    return PageResponse(data=body)


class Files:
    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return "/".join([f"/workspaces/slug:{self._workspace_id}/files", *segments])
    def list(self, *, limit: Optional[int] = None) -> SyncCursorPage[Any]:
        # The files API numbers its pages from 0.
        return SyncCursorPage(self._client, "GET", self._path(), extractor=_list_extractor, page_size=limit or 20, start_page=0)
    def upload(self, file: FileInput, *, filename: Optional[str] = None, content_type: Optional[str] = None, metadata: Optional[dict[str, Any]] = None) -> Any:
        return self._client.post(self._path(), files=_upload_parts(file, filename, content_type, metadata))[0]
    def get(self, file_id: str) -> Any:
        return self._client.get(self._path(file_id))
    def delete(self, file_id: str) -> None:
        self._client.delete(self._path(file_id))
    def download(self, file_id: str) -> Any:
        path = self.get(file_id)["path"]
        return self._client.request("GET", f"/files/{quote(path)}", raw=True)

class AsyncFiles:
    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id
    def _path(self, *segments: str) -> str:
        return "/".join([f"/workspaces/slug:{self._workspace_id}/files", *segments])
    def list(self, *, limit: Optional[int] = None) -> AsyncCursorPage[Any]:
        # The files API numbers its pages from 0.
        return AsyncCursorPage(self._client, "GET", self._path(), extractor=_list_extractor, page_size=limit or 20, start_page=0)
    async def upload(self, file: FileInput, *, filename: Optional[str] = None, content_type: Optional[str] = None, metadata: Optional[dict[str, Any]] = None) -> Any:
        return (await self._client.post(self._path(), files=_upload_parts(file, filename, content_type, metadata)))[0]
    async def get(self, file_id: str) -> Any:
        return await self._client.get(self._path(file_id))
    async def delete(self, file_id: str) -> None:
        await self._client.delete(self._path(file_id))
    async def download(self, file_id: str) -> Any:
        path = (await self.get(file_id))["path"]
        return await self._client.request("GET", f"/files/{quote(path)}", raw=True)
