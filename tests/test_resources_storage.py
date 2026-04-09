"""Tests for Files, VectorStores, VSFiles, VSAccess, Skills, Stats resources."""

from unittest.mock import MagicMock
import pytest

from prismeai.resources.files import Files
from prismeai.resources.vector_stores.vector_stores import VectorStores
from prismeai.resources.vector_stores.vs_files import VSFiles
from prismeai.resources.vector_stores.vs_access import VSAccess
from prismeai.resources.skills import Skills
from prismeai.resources.stats import Stats
from prismeai._pagination import SyncCursorPage


WS = "test-ws-id"


def _mock_client():
    client = MagicMock()
    client.get = MagicMock(return_value={"id": "test"})
    client.post = MagicMock(return_value={"id": "test"})
    client.patch = MagicMock(return_value={"id": "test"})
    client.delete = MagicMock(return_value=None)
    client.request = MagicMock(return_value=MagicMock())
    return client


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

class TestFiles:
    def test_path(self):
        f = Files(_mock_client(), WS)
        assert f._path("files") == f"/workspaces/slug:{WS}/webhooks/v1/files"

    def test_list(self):
        client = _mock_client()
        f = Files(client, WS)
        page = f.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        f = Files(client, WS)
        page = f.list(page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_upload_with_bytes(self):
        client = _mock_client()
        f = Files(client, WS)
        result = f.upload(b"file content", filename="test.txt", content_type="text/plain")
        client.post.assert_called_once()
        args, kwargs = client.post.call_args
        assert args[0] == f"/workspaces/slug:{WS}/webhooks/v1/files"
        assert "files" in kwargs
        file_tuple = kwargs["files"]["file"]
        assert file_tuple[0] == "test.txt"
        assert file_tuple[1] == b"file content"
        assert file_tuple[2] == "text/plain"

    def test_upload_with_tuple(self):
        client = _mock_client()
        f = Files(client, WS)
        result = f.upload(("myfile.pdf", b"pdf data"))
        client.post.assert_called_once()
        args, kwargs = client.post.call_args
        file_tuple = kwargs["files"]["file"]
        assert file_tuple[0] == "myfile.pdf"
        assert file_tuple[1] == b"pdf data"

    def test_get(self):
        client = _mock_client()
        f = Files(client, WS)
        result = f.get("file-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/files/file-1")

    def test_delete(self):
        client = _mock_client()
        f = Files(client, WS)
        f.delete("file-1")
        client.delete.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/files/file-1")

    def test_download(self):
        client = _mock_client()
        f = Files(client, WS)
        result = f.download("file-1")
        client.request.assert_called_once_with(
            "GET",
            f"/workspaces/slug:{WS}/webhooks/v1/files/file-1/content",
            raw=True,
        )


# ---------------------------------------------------------------------------
# VectorStores
# ---------------------------------------------------------------------------

class TestVectorStores:
    def test_init_has_sub_resources(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        assert isinstance(vs.files, VSFiles)
        assert isinstance(vs.access, VSAccess)

    def test_path(self):
        vs = VectorStores(_mock_client(), WS)
        assert vs._path("vector_stores") == f"/workspaces/slug:{WS}/webhooks/v1/vector_stores"

    def test_list(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        page = vs.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        page = vs.list(page=2, limit=10)
        assert page._page_size == 10
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        result = vs.create(name="my-store", model="text-embedding-3-small")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores",
            json={"name": "my-store", "model": "text-embedding-3-small"},
        )

    def test_get(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        result = vs.get("vs-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1")

    def test_update(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        result = vs.update("vs-1", name="updated")
        client.patch.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1",
            json={"name": "updated"},
        )

    def test_delete(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        vs.delete("vs-1")
        client.delete.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1")

    def test_search(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        result = vs.search("vs-1", query="hello world", limit=5)
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/search",
            json={"query": "hello world", "limit": 5},
        )

    def test_reindex(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        vs.reindex("vs-1")
        client.post.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/reindex")

    def test_crawl_status(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        result = vs.crawl_status("vs-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/crawl_status")

    def test_recrawl(self):
        client = _mock_client()
        vs = VectorStores(client, WS)
        vs.recrawl("vs-1")
        client.post.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/recrawl")


# ---------------------------------------------------------------------------
# VSFiles
# ---------------------------------------------------------------------------

class TestVSFiles:
    def test_path(self):
        vsf = VSFiles(_mock_client(), WS)
        assert vsf._path("vector_stores", "vs-1", "files") == f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/files"

    def test_list(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        page = vsf.list("vs-1")
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        page = vsf.list("vs-1", page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_add(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        result = vsf.add("vs-1", url="https://example.com/doc.pdf")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/files",
            json={"url": "https://example.com/doc.pdf"},
        )

    def test_delete(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        vsf.delete("vs-1", "file-1")
        client.delete.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/files/file-1"
        )

    def test_chunks(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        result = vsf.chunks("vs-1", "file-1")
        client.get.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/files/file-1/chunks"
        )

    def test_reindex(self):
        client = _mock_client()
        vsf = VSFiles(client, WS)
        vsf.reindex("vs-1", "file-1")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/files/file-1/reindex"
        )


# ---------------------------------------------------------------------------
# VSAccess
# ---------------------------------------------------------------------------

class TestVSAccess:
    def test_list(self):
        client = _mock_client()
        vsa = VSAccess(client, WS)
        page = vsa.list("vs-1")
        assert isinstance(page, SyncCursorPage)

    def test_grant(self):
        client = _mock_client()
        vsa = VSAccess(client, WS)
        result = vsa.grant("vs-1", userId="user-1", role="reader")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/access",
            json={"userId": "user-1", "role": "reader"},
        )

    def test_revoke(self):
        client = _mock_client()
        vsa = VSAccess(client, WS)
        vsa.revoke("vs-1", "user", "user-123")
        client.delete.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/vector_stores/vs-1/access/user/user-123"
        )


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class TestSkills:
    def test_path(self):
        s = Skills(_mock_client(), WS)
        assert s._path("skills") == f"/workspaces/slug:{WS}/webhooks/v1/skills"

    def test_list(self):
        client = _mock_client()
        s = Skills(client, WS)
        page = s.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        s = Skills(client, WS)
        page = s.list(page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        s = Skills(client, WS)
        result = s.create(name="my-skill", description="does stuff")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/skills",
            json={"name": "my-skill", "description": "does stuff"},
        )

    def test_get(self):
        client = _mock_client()
        s = Skills(client, WS)
        result = s.get("skill-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/skills/skill-1")

    def test_update(self):
        client = _mock_client()
        s = Skills(client, WS)
        result = s.update("skill-1", name="updated-skill")
        client.patch.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/skills/skill-1",
            json={"name": "updated-skill"},
        )

    def test_delete(self):
        client = _mock_client()
        s = Skills(client, WS)
        s.delete("skill-1")
        client.delete.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/skills/skill-1")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

class TestStats:
    def test_path(self):
        s = Stats(_mock_client(), WS)
        assert s._path("stats") == f"/workspaces/slug:{WS}/webhooks/v1/stats"

    def test_get_no_params(self):
        client = _mock_client()
        s = Stats(client, WS)
        result = s.get()
        client.get.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/stats",
            params={},
        )

    def test_get_with_period(self):
        client = _mock_client()
        s = Stats(client, WS)
        result = s.get(period="30d")
        client.get.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/stats",
            params={"period": "30d"},
        )
