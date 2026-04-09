from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, List, Optional, Union, TYPE_CHECKING

from ..._streaming import Stream, AsyncStream

if TYPE_CHECKING:
    from ..._client import SyncAPIClient, AsyncAPIClient


class FileAttachment:
    """Describes a file to attach to a message.

    Provide exactly one of ``data``, ``path``, or ``url``.

    Parameters:
        data: Raw bytes or a base64-encoded string.
        path: Local filesystem path to read.
        url: Remote URL reference (sent as-is, no encoding).
        mime_type: MIME type (guessed from *path*/*filename* when omitted).
        filename: Display name for the attachment.
        type: One of ``"file"``, ``"image"``, or ``"audio"``.
    """

    def __init__(
        self,
        *,
        data: Union[bytes, str, None] = None,
        path: Union[str, Path, None] = None,
        url: Optional[str] = None,
        mime_type: Optional[str] = None,
        filename: Optional[str] = None,
        type: str = "file",
    ) -> None:
        self.data = data
        self.path = path
        self.url = url
        self.mime_type = mime_type
        self.filename = filename
        self.type = type


def _file_attachments_to_parts(files: List[FileAttachment]) -> List[dict[str, Any]]:
    """Convert a list of FileAttachment objects into MessagePart dicts."""
    parts: List[dict[str, Any]] = []
    for f in files:
        part: dict[str, Any] = {}

        if f.url is not None:
            # URL reference -- no encoding needed
            part["url"] = f.url
            if f.mime_type:
                part["mediaType"] = f.mime_type
            if f.filename:
                part["filename"] = f.filename
        elif f.path is not None:
            # Read from local path and base64-encode
            p = Path(f.path)
            raw_bytes = p.read_bytes()
            mime = f.mime_type or mimetypes.guess_type(str(p))[0] or "application/octet-stream"
            part["raw"] = base64.b64encode(raw_bytes).decode("ascii")
            part["mediaType"] = mime
            part["filename"] = f.filename or p.name
            part["metadata"] = {"encoding": "base64"}
        elif f.data is not None:
            # Raw bytes or already-encoded string
            if isinstance(f.data, bytes):
                part["raw"] = base64.b64encode(f.data).decode("ascii")
            else:
                # Assume already base64-encoded
                part["raw"] = f.data
            if f.mime_type:
                part["mediaType"] = f.mime_type
            if f.filename:
                part["filename"] = f.filename
            part["metadata"] = {"encoding": "base64"}
        else:
            raise ValueError("FileAttachment must have at least one of data, path, or url")

        parts.append(part)
    return parts


def _inject_file_parts(kwargs: dict[str, Any], files: Optional[List[FileAttachment]]) -> dict[str, Any]:
    """Merge file attachment parts into the message kwargs before sending."""
    if not files:
        return kwargs

    file_parts = _file_attachments_to_parts(files)

    # Ensure message.parts exists and append file parts
    message = kwargs.get("message")
    if message is None:
        message = {}
        kwargs["message"] = message

    existing_parts = message.get("parts")
    if existing_parts is None:
        existing_parts = []
        message["parts"] = existing_parts

    existing_parts.extend(file_parts)
    return kwargs


class Messages:
    """Agent messages resource (sync)."""

    def __init__(self, client: SyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"

    def send(self, agent_id: str, *, files: Optional[List[FileAttachment]] = None, **kwargs: Any) -> Any:
        """Send a message and get a complete response.

        Parameters:
            agent_id: Target agent.
            files: Optional list of :class:`FileAttachment` objects.  Each
                   attachment is base64-encoded (when *data* or *path* is
                   given) and appended to ``message.parts`` in the JSON body.
            **kwargs: Remaining fields forwarded to the API (e.g. ``message``,
                      ``conversation_id``, ``context``).
        """
        kwargs = _inject_file_parts(kwargs, files)
        return self._client.post(
            self._path("agents", agent_id, "messages", "send"),
            json=kwargs,
        )

    def stream(self, agent_id: str, *, files: Optional[List[FileAttachment]] = None, **kwargs: Any) -> Stream[Any]:
        """Send a message and receive an SSE stream.

        Parameters:
            agent_id: Target agent.
            files: Optional list of :class:`FileAttachment` objects.
            **kwargs: Remaining fields forwarded to the API.
        """
        kwargs = _inject_file_parts(kwargs, files)
        response = self._client.request(
            "POST",
            self._path("agents", agent_id, "messages", "stream"),
            json=kwargs,
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        return Stream(response)


class AsyncMessages:
    """Agent messages resource (async)."""

    def __init__(self, client: AsyncAPIClient, workspace_id: str) -> None:
        self._client = client
        self._workspace_id = workspace_id

    def _path(self, *segments: str) -> str:
        parts = "/".join(segments)
        return f"/workspaces/slug:{self._workspace_id}/webhooks/v1/{parts}"

    async def send(self, agent_id: str, *, files: Optional[List[FileAttachment]] = None, **kwargs: Any) -> Any:
        """Send a message and get a complete response.

        Parameters:
            agent_id: Target agent.
            files: Optional list of :class:`FileAttachment` objects.
            **kwargs: Remaining fields forwarded to the API.
        """
        kwargs = _inject_file_parts(kwargs, files)
        return await self._client.post(
            self._path("agents", agent_id, "messages", "send"),
            json=kwargs,
        )

    async def stream(self, agent_id: str, *, files: Optional[List[FileAttachment]] = None, **kwargs: Any) -> AsyncStream[Any]:
        """Send a message and receive an SSE stream.

        Parameters:
            agent_id: Target agent.
            files: Optional list of :class:`FileAttachment` objects.
            **kwargs: Remaining fields forwarded to the API.
        """
        kwargs = _inject_file_parts(kwargs, files)
        response = await self._client.request(
            "POST",
            self._path("agents", agent_id, "messages", "stream"),
            json=kwargs,
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        return AsyncStream(response)
