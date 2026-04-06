from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Union, Tuple, Optional
import mimetypes

# Supported file input types
FileInput = Union[BinaryIO, bytes, Path, str, Tuple[str, BinaryIO], Tuple[str, bytes]]


def prepare_file(
    field_name: str,
    file_input: FileInput,
    *,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
) -> dict[str, tuple[str, Union[bytes, BinaryIO], str]]:
    """Convert a FileInput into a dict suitable for httpx file upload."""
    if isinstance(file_input, tuple):
        if len(file_input) == 2:
            name, data = file_input
            fname = filename or name
            ct = content_type or _mime_from_filename(fname)
            if isinstance(data, bytes):
                return {field_name: (fname, data, ct)}
            return {field_name: (fname, data, ct)}
        raise TypeError(f"Unsupported tuple length: {len(file_input)}")

    if isinstance(file_input, (str, Path)):
        path = Path(file_input)
        fname = filename or path.name
        ct = content_type or _mime_from_filename(fname)
        return {field_name: (fname, path.read_bytes(), ct)}

    if isinstance(file_input, bytes):
        fname = filename or "file"
        ct = content_type or "application/octet-stream"
        return {field_name: (fname, file_input, ct)}

    # BinaryIO
    fname = filename or getattr(file_input, "name", "file")
    if isinstance(fname, (Path,)):
        fname = fname.name
    ct = content_type or _mime_from_filename(str(fname))
    return {field_name: (fname, file_input, ct)}


def _mime_from_filename(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"
