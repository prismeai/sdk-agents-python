"""Tests for Files, KnowledgeBases, KBDocuments, KBAccess, KBWebSources, Skills, Stats resources."""

import asyncio
import json
from unittest.mock import MagicMock
import pytest
import httpx
import respx

from prismeai._client import SyncAPIClient, AsyncAPIClient
from prismeai.resources.files import Files, AsyncFiles
from prismeai.resources.knowledge_bases import KnowledgeBases, KBDocuments, KBAccess, KBWebSources, AsyncKBDocuments
from prismeai.resources.skills import Skills
from prismeai.resources.stats import Stats
from prismeai._pagination import SyncCursorPage


WS = "test-ws-id"
KB = f"/workspaces/slug:{WS}/webhooks/v1/knowledge_bases"
FILES = f"/workspaces/slug:{WS}/files"


def _mock_client():
    client = MagicMock()
    client.get = MagicMock(return_value={"id": "test"})
    client.post = MagicMock(return_value={"id": "test"})
    client.patch = MagicMock(return_value={"id": "test"})
    client.delete = MagicMock(return_value=None)
    client.request = MagicMock(return_value=MagicMock())
    return client


# ---------------------------------------------------------------------------
# Files (platform native files API of the storage workspace)
# ---------------------------------------------------------------------------

class TestFiles:
    def test_path(self):
        f = Files(_mock_client(), WS)
        assert f._path() == FILES
        assert f._path("file-1") == f"{FILES}/file-1"

    @respx.mock
    def test_upload_sends_private_multipart_and_returns_first_file(self):
        route = respx.post(f"https://api.test/v2{FILES}").mock(
            return_value=httpx.Response(200, json=[{"id": "file-1", "path": "ws/file-1.test.txt"}])
        )
        api = SyncAPIClient(base_url="https://api.test/v2", headers={}, max_retries=0)
        result = Files(api, WS).upload(
            b"file content", filename="test.txt", content_type="text/plain", metadata={"team": "docs"}
        )
        assert result == {"id": "file-1", "path": "ws/file-1.test.txt"}
        body = route.calls.last.request.read().decode()
        assert 'name="file"; filename="test.txt"' in body
        assert 'name="public"\r\n\r\nfalse\r\n' in body
        assert f'name="metadata"\r\n\r\n{json.dumps({"team": "docs"})}\r\n' in body
        assert "shareToken" not in body
        assert "expiresAfter" not in body

    def test_upload_without_metadata(self):
        client = _mock_client()
        client.post.return_value = [{"id": "file-1"}]
        result = Files(client, WS).upload(("myfile.pdf", b"pdf data"))
        assert result == {"id": "file-1"}
        args, kwargs = client.post.call_args
        assert args[0] == FILES
        assert kwargs["files"]["file"][:2] == ("myfile.pdf", b"pdf data")
        assert kwargs["files"]["public"] == (None, "false")
        assert "metadata" not in kwargs["files"]

    def test_get(self):
        client = _mock_client()
        Files(client, WS).get("file-1")
        client.get.assert_called_once_with(f"{FILES}/file-1")

    def test_delete_goes_through_the_storage_route(self):
        client = _mock_client()
        client.delete.return_value = {"deleted": True, "file_purged": True, "purge_reason": "DELETED"}
        assert Files(client, WS).delete("file-1")["file_purged"] is True
        client.delete.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/files/file-1")

    @respx.mock
    def test_async_upload_and_download(self):
        respx.post(f"https://api.test/v2{FILES}").mock(
            return_value=httpx.Response(200, json=[{"id": "file-1", "path": "ws/file-1.my report.pdf"}])
        )
        respx.get(f"https://api.test/v2{FILES}/file-1").mock(
            return_value=httpx.Response(200, json={"id": "file-1", "path": "ws/file-1.my report.pdf"})
        )
        content = respx.get("https://api.test/v2/files/ws/file-1.my%20report.pdf").mock(
            return_value=httpx.Response(200, content=b"pdf")
        )

        async def run():
            api = AsyncAPIClient(base_url="https://api.test/v2", headers={}, max_retries=0)
            files = AsyncFiles(api, WS)
            uploaded = await files.upload(b"pdf", filename="my report.pdf")
            response = await files.download(uploaded["id"])
            return uploaded, response

        uploaded, response = asyncio.run(run())
        assert uploaded["id"] == "file-1"
        assert response.content == b"pdf"
        assert content.called

    def test_download_fetches_file_path_through_api(self):
        client = _mock_client()
        client.get.return_value = {"id": "file-1", "path": "ws/file-1.my report.pdf"}
        Files(client, WS).download("file-1")
        client.get.assert_called_once_with(f"{FILES}/file-1")
        client.request.assert_called_once_with("GET", "/files/ws/file-1.my%20report.pdf", raw=True)


# ---------------------------------------------------------------------------
# KnowledgeBases
# ---------------------------------------------------------------------------

class TestKnowledgeBases:
    def test_init_has_sub_resources(self):
        kb = KnowledgeBases(_mock_client(), WS)
        assert isinstance(kb.documents, KBDocuments)
        assert isinstance(kb.access, KBAccess)
        assert isinstance(kb.web_sources, KBWebSources)

    def test_path(self):
        kb = KnowledgeBases(_mock_client(), WS)
        assert kb._path("knowledge_bases") == KB

    def test_list(self):
        page = KnowledgeBases(_mock_client(), WS).list()
        assert isinstance(page, SyncCursorPage)
        assert page._path == KB

    def test_list_with_params(self):
        page = KnowledgeBases(_mock_client(), WS).list(page=2, limit=10)
        assert page._page_size == 10
        assert page._start_page == 2

    def test_list_with_filters(self):
        client = _mock_client()
        KnowledgeBases(client, WS).list(scope="owned,shared", status="active", search="faq").get_page()
        assert client.request.call_args.kwargs["params"] == {
            "name": None, "search": "faq", "agent_id": None, "scope": "owned,shared", "status": "active",
            "page": 1, "limit": 20,
        }

    def test_create(self):
        client = _mock_client()
        KnowledgeBases(client, WS).create(name="my-kb", description="docs")
        client.post.assert_called_once_with(KB, json={"name": "my-kb", "description": "docs"})

    def test_get(self):
        client = _mock_client()
        KnowledgeBases(client, WS).get("vs_1")
        client.get.assert_called_once_with(f"{KB}/vs_1", params={"include": None})

    def test_get_include_processing(self):
        client = _mock_client()
        KnowledgeBases(client, WS).get("vs_1", include="processing")
        client.get.assert_called_once_with(f"{KB}/vs_1", params={"include": "processing"})

    def test_update(self):
        client = _mock_client()
        KnowledgeBases(client, WS).update("vs_1", name="updated")
        client.patch.assert_called_once_with(f"{KB}/vs_1", json={"name": "updated"})

    def test_delete(self):
        client = _mock_client()
        KnowledgeBases(client, WS).delete("vs_1")
        client.delete.assert_called_once_with(f"{KB}/vs_1")

    def test_search(self):
        client = _mock_client()
        KnowledgeBases(client, WS).search("vs_1", query="hello world", limit=5)
        client.post.assert_called_once_with(
            f"{KB}/vs_1/search", json={"query": "hello world", "limit": 5}
        )

    def test_reindex(self):
        client = _mock_client()
        KnowledgeBases(client, WS).reindex("vs_1", reset_chunking_overrides=True)
        client.post.assert_called_once_with(
            f"{KB}/vs_1/reindex", json={"reset_chunking_overrides": True}
        )


# ---------------------------------------------------------------------------
# KBDocuments
# ---------------------------------------------------------------------------

class TestKBDocuments:
    def test_list(self):
        page = KBDocuments(_mock_client(), WS).list("vs_1", page=2, limit=5)
        assert isinstance(page, SyncCursorPage)
        assert page._path == f"{KB}/vs_1/documents"
        assert page._page_size == 5
        assert page._start_page == 2

    def test_list_with_filters_and_tags(self):
        client = _mock_client()
        KBDocuments(client, WS).list(
            "vs_1", status="failed,rejected", source_type="web_page", updated_before=1700000000,
            tags={"project": "x", "team": "docs"},
        ).get_page()
        params = client.request.call_args.kwargs["params"]
        assert params["status"] == "failed,rejected"
        assert params["source_type"] == "web_page"
        assert params["updated_before"] == 1700000000
        assert params["tags.project"] == "x"
        assert params["tags.team"] == "docs"
        assert "tags" not in params

    def test_list_with_owner_and_metadata(self):
        client = _mock_client()
        KBDocuments(client, WS).list("vs_1", owner_user_id="u1", metadata={"lang": "fr"}).get_page()
        params = client.request.call_args.kwargs["params"]
        assert params["owner_user_id"] == "u1"
        assert params["metadata.lang"] == "fr"
        assert "metadata" not in params

    def test_add_native_file(self):
        client = _mock_client()
        KBDocuments(client, WS).add("vs_1", native_file_id="file-1", tags={"team": "docs"})
        client.post.assert_called_once_with(
            f"{KB}/vs_1/documents", json={"native_file_id": "file-1", "tags": {"team": "docs"}}
        )

    def test_get(self):
        client = _mock_client()
        KBDocuments(client, WS).get("vs_1", "vsf_1")
        client.get.assert_called_once_with(f"{KB}/vs_1/documents/vsf_1")

    def test_update(self):
        client = _mock_client()
        KBDocuments(client, WS).update("vs_1", "vsf_1", tags={"team": "docs"}, filename="faq.md")
        client.patch.assert_called_once_with(
            f"{KB}/vs_1/documents/vsf_1", json={"tags": {"team": "docs"}, "filename": "faq.md"}
        )

    def test_delete(self):
        client = _mock_client()
        client.delete.return_value = {"id": "vsf_1", "deleted": True, "file_purged": False, "purge_reason": "NOT_OWNED"}
        assert KBDocuments(client, WS).delete("vs_1", "vsf_1")["purge_reason"] == "NOT_OWNED"
        client.delete.assert_called_once_with(f"{KB}/vs_1/documents/vsf_1")

    def test_async_delete_returns_the_body(self):
        client = MagicMock()

        async def delete(path):
            return {"id": "vsf_1", "deleted": True, "file_purged": True}
        client.delete = delete
        result = asyncio.run(AsyncKBDocuments(client, WS).delete("vs_1", "vsf_1"))
        assert result["file_purged"] is True

    def test_chunks(self):
        page = KBDocuments(_mock_client(), WS).chunks("vs_1", "vsf_1", page=2, limit=50)
        assert isinstance(page, SyncCursorPage)
        assert page._path == f"{KB}/vs_1/documents/vsf_1/chunks"
        assert (page._start_page, page._page_size) == (2, 50)

    def test_source_url(self):
        client = _mock_client()
        KBDocuments(client, WS).source_url("vs_1", "vsf_1")
        client.get.assert_called_once_with(f"{KB}/vs_1/documents/vsf_1/source_url")

    def test_reindex(self):
        client = _mock_client()
        KBDocuments(client, WS).reindex("vs_1", "vsf_1")
        client.post.assert_called_once_with(f"{KB}/vs_1/documents/vsf_1/reindex", json={})


# ---------------------------------------------------------------------------
# KBAccess
# ---------------------------------------------------------------------------

class TestKBAccess:
    def test_list(self):
        page = KBAccess(_mock_client(), WS).list("vs_1", limit=100)
        assert isinstance(page, SyncCursorPage)
        assert page._path == f"{KB}/vs_1/access"
        assert page._page_size == 100

    def test_grant(self):
        client = _mock_client()
        KBAccess(client, WS).grant("vs_1", principal_type="user", principal_id="user-1", role="reader")
        client.post.assert_called_once_with(
            f"{KB}/vs_1/access",
            json={"principal_type": "user", "principal_id": "user-1", "role": "reader"},
        )

    def test_update(self):
        client = _mock_client()
        KBAccess(client, WS).update("vs_1", "group", "team-standard", role="editor")
        client.patch.assert_called_once_with(
            f"{KB}/vs_1/access/group/team-standard", json={"role": "editor"}
        )

    def test_revoke(self):
        client = _mock_client()
        KBAccess(client, WS).revoke("vs_1", "user", "user-123")
        client.delete.assert_called_once_with(f"{KB}/vs_1/access/user/user-123")


# ---------------------------------------------------------------------------
# KBWebSources
# ---------------------------------------------------------------------------

class TestKBWebSources:
    def test_list(self):
        page = KBWebSources(_mock_client(), WS).list("vs_1")
        assert isinstance(page, SyncCursorPage)
        assert page._path == f"{KB}/vs_1/web_sources"

    def test_add(self):
        client = _mock_client()
        KBWebSources(client, WS).add("vs_1", url="https://example.com/docs")
        client.post.assert_called_once_with(
            f"{KB}/vs_1/web_sources", json={"url": "https://example.com/docs"}
        )

    def test_get(self):
        client = _mock_client()
        KBWebSources(client, WS).get("vs_1", "seed_1")
        client.get.assert_called_once_with(f"{KB}/vs_1/web_sources/seed_1")

    def test_delete(self):
        client = _mock_client()
        KBWebSources(client, WS).delete("vs_1", "seed_1")
        client.delete.assert_called_once_with(f"{KB}/vs_1/web_sources/seed_1")


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
