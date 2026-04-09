"""Tests for Artifacts, Shares, Ratings, Activity, Profiles, Orgs resources."""

from unittest.mock import MagicMock
import pytest

from prismeai.resources.artifacts import Artifacts
from prismeai.resources.shares import Shares
from prismeai.resources.ratings import Ratings
from prismeai.resources.activity import Activity
from prismeai.resources.profiles import Profiles
from prismeai.resources.orgs import Orgs
from prismeai._pagination import SyncCursorPage


WS = "test-ws-id"


def _mock_client():
    client = MagicMock()
    client.get = MagicMock(return_value={"id": "test"})
    client.post = MagicMock(return_value={"id": "test"})
    client.patch = MagicMock(return_value={"id": "test"})
    client.delete = MagicMock(return_value=None)
    return client


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

class TestArtifacts:
    def test_path(self):
        a = Artifacts(_mock_client(), WS)
        assert a._path("artifacts") == f"/workspaces/slug:{WS}/webhooks/v1/artifacts"

    def test_list(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        page = a.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        page = a.list(page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_get(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        result = a.get("art-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/artifacts/art-1")

    def test_update(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        result = a.update("art-1", title="Updated Artifact")
        client.patch.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/artifacts/art-1",
            json={"title": "Updated Artifact"},
        )

    def test_delete(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        a.delete("art-1")
        client.delete.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/artifacts/art-1")

    def test_shares(self):
        client = _mock_client()
        a = Artifacts(client, WS)
        a.shares("art-1", public=True)
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/artifacts/art-1/shares",
            json={"public": True},
        )


# ---------------------------------------------------------------------------
# Shares
# ---------------------------------------------------------------------------

class TestShares:
    def test_path(self):
        s = Shares(_mock_client(), WS)
        assert s._path("shares") == f"/workspaces/slug:{WS}/webhooks/v1/shares"

    def test_list(self):
        client = _mock_client()
        s = Shares(client, WS)
        page = s.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        s = Shares(client, WS)
        page = s.list(page=3, limit=10)
        assert page._page_size == 10
        assert page._start_page == 3

    def test_get(self):
        client = _mock_client()
        s = Shares(client, WS)
        result = s.get("share-1")
        client.get.assert_called_once_with(f"/workspaces/slug:{WS}/webhooks/v1/shares/share-1")


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------

class TestRatings:
    def test_path(self):
        r = Ratings(_mock_client(), WS)
        assert r._path("ratings") == f"/workspaces/slug:{WS}/webhooks/v1/ratings"

    def test_create(self):
        client = _mock_client()
        r = Ratings(client, WS)
        result = r.create("agent-1", score=5, comment="Excellent", messageId="msg-1")
        client.post.assert_called_once_with(
            f"/workspaces/slug:{WS}/webhooks/v1/agents/agent-1/ratings",
            json={"score": 5, "comment": "Excellent", "messageId": "msg-1"},
        )
        assert result == {"id": "test"}


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------

class TestActivity:
    def test_path(self):
        a = Activity(_mock_client(), WS)
        assert a._path("activity") == f"/workspaces/slug:{WS}/webhooks/v1/activity"

    def test_list(self):
        client = _mock_client()
        a = Activity(client, WS)
        page = a.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        a = Activity(client, WS)
        page = a.list(page=2, limit=15)
        assert page._page_size == 15
        assert page._start_page == 2


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

class TestProfiles:
    def test_path(self):
        p = Profiles(_mock_client(), WS)
        assert p._path("profiles") == f"/workspaces/slug:{WS}/webhooks/v1/profiles"

    def test_list(self):
        client = _mock_client()
        p = Profiles(client, WS)
        page = p.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_search(self):
        client = _mock_client()
        p = Profiles(client, WS)
        page = p.list(search="john")
        assert page._params == {"search": "john"}

    def test_list_with_all_params(self):
        client = _mock_client()
        p = Profiles(client, WS)
        page = p.list(page=2, limit=10, search="admin")
        assert page._params == {"search": "admin"}
        assert page._page_size == 10
        assert page._start_page == 2


# ---------------------------------------------------------------------------
# Orgs
# ---------------------------------------------------------------------------

class TestOrgs:
    def test_path(self):
        o = Orgs(_mock_client(), WS)
        assert o._path("orgs", "agents") == f"/workspaces/slug:{WS}/webhooks/v1/orgs/agents"

    def test_list_agents(self):
        client = _mock_client()
        o = Orgs(client, WS)
        page = o.list_agents("org-1")
        assert isinstance(page, SyncCursorPage)

    def test_list_agents_with_params(self):
        client = _mock_client()
        o = Orgs(client, WS)
        page = o.list_agents("org-1", page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2
