"""Tests for Tasks resource."""

from unittest.mock import MagicMock
import pytest

from prismeai.resources.tasks import Tasks
from prismeai._pagination import SyncCursorPage


WS = "test-ws-id"


def _mock_client():
    client = MagicMock()
    client.get = MagicMock(return_value={"id": "task-1", "status": "completed"})
    client.post = MagicMock(return_value={"id": "task-1", "status": "cancelled"})
    client.request = MagicMock(return_value={"results": [], "total": 0, "page": 1, "limit": 20})
    return client


class TestTasks:
    def test_path(self):
        tasks = Tasks(_mock_client(), WS)
        assert tasks._path("tasks") == f"/workspaces/{WS}/webhooks/tasks"
        assert tasks._path("tasks", "t1") == f"/workspaces/{WS}/webhooks/tasks/t1"

    def test_list_returns_cursor_page(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        page = tasks.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_default_params(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        page = tasks.list()
        assert page._params == {}
        assert page._page_size == 20
        assert page._start_page == 1

    def test_list_with_agent_id(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        page = tasks.list(agent_id="agent-x")
        assert page._params == {"agentId": "agent-x"}

    def test_list_with_status(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        page = tasks.list(status="running")
        assert page._params == {"status": "running"}

    def test_list_with_all_params(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        page = tasks.list(page=3, limit=10, agent_id="a1", status="completed")
        assert page._params == {"agentId": "a1", "status": "completed"}
        assert page._page_size == 10
        assert page._start_page == 3

    def test_get(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        result = tasks.get("task-123")
        client.get.assert_called_once_with(f"/workspaces/{WS}/webhooks/tasks/task-123")
        assert result == {"id": "task-1", "status": "completed"}

    def test_cancel(self):
        client = _mock_client()
        tasks = Tasks(client, WS)
        result = tasks.cancel("task-123")
        client.post.assert_called_once_with(f"/workspaces/{WS}/webhooks/tasks/task-123/cancel")
        assert result == {"id": "task-1", "status": "cancelled"}
