"""Tests for _files.py: prepare_file helper."""

import io
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prismeai._files import prepare_file, _mime_from_filename, FileInput


# ---------------------------------------------------------------------------
# _mime_from_filename
# ---------------------------------------------------------------------------

class TestMimeFromFilename:
    def test_txt(self):
        assert _mime_from_filename("file.txt") == "text/plain"

    def test_pdf(self):
        assert _mime_from_filename("doc.pdf") == "application/pdf"

    def test_json(self):
        assert _mime_from_filename("data.json") == "application/json"

    def test_unknown(self):
        assert _mime_from_filename("file.xyz123") == "application/octet-stream"

    def test_no_extension(self):
        assert _mime_from_filename("Makefile") == "application/octet-stream"

    def test_png(self):
        assert _mime_from_filename("image.png") == "image/png"

    def test_jpg(self):
        result = _mime_from_filename("photo.jpg")
        assert result in ("image/jpeg", "image/jpg")

    def test_html(self):
        assert _mime_from_filename("page.html") == "text/html"


# ---------------------------------------------------------------------------
# prepare_file - tuple input
# ---------------------------------------------------------------------------

class TestPrepareFileTuple:
    def test_tuple_with_bytes(self):
        result = prepare_file("file", ("test.txt", b"content"))
        assert "file" in result
        fname, data, ct = result["file"]
        assert fname == "test.txt"
        assert data == b"content"
        assert ct == "text/plain"

    def test_tuple_with_binary_io(self):
        buf = io.BytesIO(b"data")
        result = prepare_file("upload", ("report.pdf", buf))
        fname, data, ct = result["upload"]
        assert fname == "report.pdf"
        assert data is buf
        assert ct == "application/pdf"

    def test_tuple_custom_filename_override(self):
        result = prepare_file("file", ("original.txt", b"data"), filename="override.csv")
        fname, data, ct = result["file"]
        assert fname == "override.csv"
        assert ct == "text/csv"

    def test_tuple_custom_content_type(self):
        result = prepare_file("file", ("test.txt", b"data"), content_type="application/custom")
        fname, data, ct = result["file"]
        assert ct == "application/custom"

    def test_tuple_wrong_length_raises(self):
        with pytest.raises(TypeError, match="Unsupported tuple length"):
            prepare_file("file", ("a", "b", "c"))  # type: ignore


# ---------------------------------------------------------------------------
# prepare_file - path input (str or Path)
# ---------------------------------------------------------------------------

class TestPrepareFilePath:
    def test_str_path(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"hello world")
        result = prepare_file("file", str(test_file))
        fname, data, ct = result["file"]
        assert fname == "test.txt"
        assert data == b"hello world"
        assert ct == "text/plain"

    def test_path_object(self, tmp_path):
        test_file = tmp_path / "document.pdf"
        test_file.write_bytes(b"pdf content")
        result = prepare_file("file", test_file)
        fname, data, ct = result["file"]
        assert fname == "document.pdf"
        assert data == b"pdf content"
        assert ct == "application/pdf"

    def test_path_with_filename_override(self, tmp_path):
        test_file = tmp_path / "original.txt"
        test_file.write_bytes(b"data")
        result = prepare_file("file", test_file, filename="renamed.csv")
        fname, data, ct = result["file"]
        assert fname == "renamed.csv"
        assert ct == "text/csv"

    def test_path_with_content_type_override(self, tmp_path):
        test_file = tmp_path / "file.bin"
        test_file.write_bytes(b"binary data")
        result = prepare_file("file", test_file, content_type="application/x-custom")
        fname, data, ct = result["file"]
        assert ct == "application/x-custom"


# ---------------------------------------------------------------------------
# prepare_file - bytes input
# ---------------------------------------------------------------------------

class TestPrepareFileBytes:
    def test_bytes_default(self):
        result = prepare_file("file", b"raw bytes")
        fname, data, ct = result["file"]
        assert fname == "file"
        assert data == b"raw bytes"
        assert ct == "application/octet-stream"

    def test_bytes_with_filename(self):
        result = prepare_file("file", b"raw bytes", filename="data.json")
        fname, data, ct = result["file"]
        assert fname == "data.json"
        # bytes path uses application/octet-stream unless content_type is explicitly set
        assert ct == "application/octet-stream"

    def test_bytes_with_content_type(self):
        result = prepare_file("file", b"raw bytes", content_type="text/plain")
        fname, data, ct = result["file"]
        assert ct == "text/plain"


# ---------------------------------------------------------------------------
# prepare_file - BinaryIO input
# ---------------------------------------------------------------------------

class TestPrepareFileBinaryIO:
    def test_binary_io_with_name(self):
        buf = io.BytesIO(b"stream data")
        buf.name = "upload.txt"
        result = prepare_file("file", buf)
        fname, data, ct = result["file"]
        assert fname == "upload.txt"
        assert data is buf
        assert ct == "text/plain"

    def test_binary_io_without_name(self):
        buf = io.BytesIO(b"stream data")
        result = prepare_file("file", buf)
        fname, data, ct = result["file"]
        assert fname == "file"
        assert data is buf

    def test_binary_io_with_filename_override(self):
        buf = io.BytesIO(b"stream data")
        buf.name = "original.txt"
        result = prepare_file("upload", buf, filename="override.pdf")
        fname, data, ct = result["upload"]
        assert fname == "override.pdf"
        assert ct == "application/pdf"

    def test_binary_io_with_path_name(self):
        buf = io.BytesIO(b"stream data")
        buf.name = Path("/some/path/doc.txt")
        result = prepare_file("file", buf)
        fname, data, ct = result["file"]
        assert fname == "doc.txt"
        assert ct == "text/plain"

    def test_binary_io_with_content_type_override(self):
        buf = io.BytesIO(b"data")
        result = prepare_file("file", buf, content_type="image/png")
        fname, data, ct = result["file"]
        assert ct == "image/png"


# ---------------------------------------------------------------------------
# prepare_file - field name propagation
# ---------------------------------------------------------------------------

class TestPrepareFileFieldName:
    def test_custom_field_name(self):
        result = prepare_file("document", b"data")
        assert "document" in result
        assert "file" not in result

    def test_another_field_name(self):
        result = prepare_file("attachment", b"data")
        assert "attachment" in result
