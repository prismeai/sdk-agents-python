"""Tests for agents, messages, conversations, analytics, evaluations, access, tools, a2a resources."""

from unittest.mock import MagicMock, call
import pytest

from prismeai.resources.agents.agents import Agents
from prismeai.resources.agents.messages import Messages
from prismeai.resources.conversations import Conversations
from prismeai.resources.analytics import Analytics
from prismeai.resources.evaluations import Evaluations
from prismeai.resources.access import Access
from prismeai.resources.tools import Tools
from prismeai.resources.a2a import A2A
from prismeai._pagination import SyncCursorPage
from prismeai._streaming import Stream


WS = "test-ws-id"


def _mock_client():
    client = MagicMock()
    client.get = MagicMock(return_value={"id": "test", "name": "test"})
    client.post = MagicMock(return_value={"id": "test", "name": "test"})
    client.put = MagicMock(return_value={"id": "test", "name": "test"})
    client.patch = MagicMock(return_value={"id": "test", "name": "test"})
    client.delete = MagicMock(return_value=None)
    client.request = MagicMock(return_value=MagicMock())
    return client


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

class TestAgents:
    def test_init_creates_messages_sub_resource(self):
        client = _mock_client()
        agents = Agents(client, WS)
        assert isinstance(agents.messages, Messages)

    def test_path_no_segments(self):
        agents = Agents(_mock_client(), WS)
        assert agents._path() == f"/workspaces/{WS}/webhooks"

    def test_path_with_segments(self):
        agents = Agents(_mock_client(), WS)
        assert agents._path("agents", "abc") == f"/workspaces/{WS}/webhooks/agents/abc"

    def test_list_returns_cursor_page(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.list()
        assert isinstance(result, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        agents = Agents(client, WS)
        page = agents.list(page=2, limit=10, labels="a,b", search="hello")
        assert isinstance(page, SyncCursorPage)
        assert page._params == {"labels": "a,b", "search": "hello"}
        assert page._page_size == 10
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.create(name="My Agent", model="gpt-4")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents",
            json={"name": "My Agent", "model": "gpt-4"},
        )
        assert result == {"id": "test", "name": "test"}

    def test_get(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.get("agent-123")
        client.get.assert_called_once_with(f"/workspaces/{WS}/webhooks/agents/agent-123")
        assert result == {"id": "test", "name": "test"}

    def test_update(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.update("agent-123", name="Updated")
        client.patch.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-123",
            json={"name": "Updated"},
        )
        assert result == {"id": "test", "name": "test"}

    def test_delete(self):
        client = _mock_client()
        agents = Agents(client, WS)
        agents.delete("agent-123")
        client.delete.assert_called_once_with(f"/workspaces/{WS}/webhooks/agents/agent-123")

    def test_publish(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.publish("agent-123")
        client.post.assert_called_once_with(f"/workspaces/{WS}/webhooks/agents/agent-123/publish")
        assert result == {"id": "test", "name": "test"}

    def test_discard_draft(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.discard_draft("agent-123")
        client.post.assert_called_once_with(f"/workspaces/{WS}/webhooks/agents/agent-123/discard-draft")
        assert result == {"id": "test", "name": "test"}

    def test_discovery(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.discovery("agent-123", public=True)
        client.patch.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-123/discovery",
            json={"public": True},
        )
        assert result == {"id": "test", "name": "test"}

    def test_export(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.export("agent-123")
        client.get.assert_called_once_with(f"/workspaces/{WS}/webhooks/agents/agent-123/export")
        assert result == {"id": "test", "name": "test"}

    def test_import(self):
        client = _mock_client()
        agents = Agents(client, WS)
        config = {"name": "Imported", "model": "gpt-4"}
        result = agents.import_(config)
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/import",
            json=config,
        )
        assert result == {"id": "test", "name": "test"}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

class TestMessages:
    def test_path(self):
        msgs = Messages(_mock_client(), WS)
        assert msgs._path("agents", "a1", "messages") == f"/workspaces/{WS}/webhooks/agents/a1/messages"

    def test_send(self):
        client = _mock_client()
        msgs = Messages(client, WS)
        result = msgs.send("agent-1", text="Hello", conversationId="conv-1")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/messages",
            json={"text": "Hello", "conversationId": "conv-1"},
        )
        assert result == {"id": "test", "name": "test"}

    def test_stream(self):
        client = _mock_client()
        raw_response = MagicMock()
        client.request.return_value = raw_response
        msgs = Messages(client, WS)
        result = msgs.stream("agent-1", text="Hello")
        client.request.assert_called_once_with(
            "POST",
            f"/workspaces/{WS}/webhooks/agents/agent-1/messages/stream",
            json={"text": "Hello"},
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        assert isinstance(result, Stream)


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

class TestConversations:
    def test_path(self):
        convs = Conversations(_mock_client(), WS)
        assert convs._path("conversations") == f"/workspaces/{WS}/webhooks/conversations"

    def test_list_returns_cursor_page(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        page = convs.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_agent_id(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        page = convs.list(agent_id="agent-x", page=3, limit=5)
        assert page._params == {"agentId": "agent-x"}
        assert page._page_size == 5
        assert page._start_page == 3

    def test_create(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.create(agentId="a1", title="New Conversation")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/conversations",
            json={"agentId": "a1", "title": "New Conversation"},
        )

    def test_get(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.get("conv-1")
        client.get.assert_called_once_with(f"/workspaces/{WS}/webhooks/conversations/conv-1")

    def test_update(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.update("conv-1", title="Updated")
        client.patch.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/conversations/conv-1",
            json={"title": "Updated"},
        )

    def test_delete(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        convs.delete("conv-1")
        client.delete.assert_called_once_with(f"/workspaces/{WS}/webhooks/conversations/conv-1")

    def test_messages_returns_cursor_page(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        page = convs.messages("conv-1", page=2, limit=10)
        assert isinstance(page, SyncCursorPage)
        assert page._page_size == 10
        assert page._start_page == 2

    def test_share(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        convs.share("conv-1", public=True)
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/conversations/conv-1/share",
            json={"public": True},
        )


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class TestAnalytics:
    def test_path(self):
        a = Analytics(_mock_client(), WS)
        assert a._path("agents", "a1", "analytics") == f"/workspaces/{WS}/webhooks/agents/a1/analytics"

    def test_get_no_params(self):
        client = _mock_client()
        a = Analytics(client, WS)
        result = a.get("agent-1")
        client.get.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/analytics",
            params={},
        )

    def test_get_with_params(self):
        client = _mock_client()
        a = Analytics(client, WS)
        result = a.get("agent-1", period="7d", granularity="day")
        client.get.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/analytics",
            params={"period": "7d", "granularity": "day"},
        )


# ---------------------------------------------------------------------------
# Evaluations
# ---------------------------------------------------------------------------

class TestEvaluations:
    def test_list_returns_cursor_page(self):
        client = _mock_client()
        ev = Evaluations(client, WS)
        page = ev.list("agent-1")
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        ev = Evaluations(client, WS)
        page = ev.list("agent-1", page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        ev = Evaluations(client, WS)
        result = ev.create("agent-1", score=0.95, comment="great")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/evaluations",
            json={"score": 0.95, "comment": "great"},
        )


# ---------------------------------------------------------------------------
# Access
# ---------------------------------------------------------------------------

class TestAccess:
    def test_list(self):
        client = _mock_client()
        acc = Access(client, WS)
        page = acc.list("agent-1")
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        acc = Access(client, WS)
        page = acc.list("agent-1", page=3, limit=15)
        assert page._page_size == 15
        assert page._start_page == 3

    def test_grant(self):
        client = _mock_client()
        acc = Access(client, WS)
        result = acc.grant("agent-1", userId="user-1", role="reader")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/access",
            json={"userId": "user-1", "role": "reader"},
        )

    def test_revoke(self):
        client = _mock_client()
        acc = Access(client, WS)
        acc.revoke("agent-1", "access-id-1")
        client.delete.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/access/access-id-1"
        )

    def test_request_access(self):
        client = _mock_client()
        acc = Access(client, WS)
        result = acc.request_access("agent-1")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/access-requests"
        )

    def test_list_requests(self):
        client = _mock_client()
        acc = Access(client, WS)
        page = acc.list_requests("agent-1", page=1, limit=10)
        assert isinstance(page, SyncCursorPage)
        assert page._page_size == 10

    def test_handle_request(self):
        client = _mock_client()
        acc = Access(client, WS)
        result = acc.handle_request("agent-1", "req-1", "approve")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/access-requests/req-1/approve"
        )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class TestTools:
    def test_list(self):
        client = _mock_client()
        tools = Tools(client, WS)
        page = tools.list()
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        tools = Tools(client, WS)
        page = tools.list(page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        tools = Tools(client, WS)
        result = tools.create(name="my-tool", type="function")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/tools",
            json={"name": "my-tool", "type": "function"},
        )

    def test_get(self):
        client = _mock_client()
        tools = Tools(client, WS)
        result = tools.get("tool-1")
        client.get.assert_called_once_with(f"/workspaces/{WS}/webhooks/tools/tool-1")


# ---------------------------------------------------------------------------
# A2A
# ---------------------------------------------------------------------------

class TestA2A:
    def test_send(self):
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.send("agent-1", message="Hello", taskId="t-1")
        client.post.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/a2a/send",
            json={"message": "Hello", "taskId": "t-1"},
        )

    def test_send_subscribe(self):
        client = _mock_client()
        raw_response = MagicMock()
        client.request.return_value = raw_response
        a2a = A2A(client, WS)
        result = a2a.send_subscribe("agent-1", message="Hello")
        client.request.assert_called_once_with(
            "POST",
            f"/workspaces/{WS}/webhooks/agents/agent-1/a2a/send-subscribe",
            json={"message": "Hello"},
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        assert isinstance(result, Stream)

    def test_get_card(self):
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.get_card("agent-1")
        client.get.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/a2a/card"
        )

    def test_get_extended_card(self):
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.get_extended_card("agent-1")
        client.get.assert_called_once_with(
            f"/workspaces/{WS}/webhooks/agents/agent-1/a2a/card/extended"
        )
