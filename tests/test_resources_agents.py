"""Tests for agents, messages, conversations, analytics, evaluations, access, tools, a2a resources."""

from unittest.mock import MagicMock, call, ANY
import pytest

from prismeai.resources.agents.agents import Agents
from prismeai.resources.agents.messages import Messages, _file_attachments_to_parts, FileAttachment
from prismeai.resources.conversations import Conversations
from prismeai.resources.analytics import Analytics
from prismeai.resources.evaluations import Evaluations
from prismeai.resources.access import Access
from prismeai.resources.tools import Tools
from prismeai.resources.a2a import A2A
from prismeai._pagination import SyncCursorPage
from prismeai._streaming import Stream


WS = "test-ws-id"

def _p(*segments):
    """Build expected path like resources do: /workspaces/slug:{WS}/webhooks/v1/..."""
    s = "/".join(segments)
    return f"/workspaces/slug:{WS}/webhooks/v1/{s}" if s else f"/workspaces/slug:{WS}/webhooks/v1"


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
        assert agents._path() == f"/workspaces/slug:{WS}/webhooks/v1"

    def test_path_with_segments(self):
        agents = Agents(_mock_client(), WS)
        assert agents._path("agents", "abc") == _p("agents", "abc")

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
            _p("agents"),
            json={"name": "My Agent", "model": "gpt-4"},
        )
        assert result == {"id": "test", "name": "test"}

    def test_get(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.get("agent-123")
        client.get.assert_called_once_with(_p("agents", "agent-123"))
        assert result == {"id": "test", "name": "test"}

    def test_update(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.update("agent-123", name="Updated")
        client.patch.assert_called_once_with(
            _p("agents", "agent-123"),
            json={"name": "Updated"},
        )
        assert result == {"id": "test", "name": "test"}

    def test_delete(self):
        client = _mock_client()
        agents = Agents(client, WS)
        agents.delete("agent-123")
        client.delete.assert_called_once_with(_p("agents", "agent-123"))

    def test_publish(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.publish("agent-123")
        client.post.assert_called_once_with(_p("agents", "agent-123", "publish"))
        assert result == {"id": "test", "name": "test"}

    def test_discard_draft(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.discard_draft("agent-123")
        client.post.assert_called_once_with(_p("agents", "agent-123", "discard-draft"))
        assert result == {"id": "test", "name": "test"}

    def test_discovery_returns_cursor_page(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.discovery()
        assert isinstance(result, SyncCursorPage)

    def test_export(self):
        client = _mock_client()
        agents = Agents(client, WS)
        result = agents.export("agent-123")
        client.get.assert_called_once_with(_p("agents", "agent-123", "export"))
        assert result == {"id": "test", "name": "test"}

    def test_import_with_string(self):
        """Import wraps YAML string in agents_md envelope."""
        client = _mock_client()
        agents = Agents(client, WS)
        yaml_str = "name: My Agent\nmodel: gpt-4"
        result = agents.import_(yaml_str)
        client.post.assert_called_once_with(
            _p("agents", "import"),
            json={"agents_md": yaml_str},
        )
        assert result == {"id": "test", "name": "test"}

    def test_import_with_dict(self):
        """Import also wraps dict in agents_md envelope."""
        client = _mock_client()
        agents = Agents(client, WS)
        config = {"name": "Imported", "model": "gpt-4"}
        result = agents.import_(config)
        client.post.assert_called_once_with(
            _p("agents", "import"),
            json={"agents_md": config},
        )
        assert result == {"id": "test", "name": "test"}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

class TestMessages:
    def test_path(self):
        msgs = Messages(_mock_client(), WS)
        assert msgs._path("agents", "a1", "messages") == _p("agents", "a1", "messages")

    def test_send(self):
        client = _mock_client()
        msgs = Messages(client, WS)
        result = msgs.send("agent-1", message={"parts": [{"text": "Hello"}]})
        client.post.assert_called_once_with(
            _p("agents", "agent-1", "messages", "send"),
            json={"message": {"parts": [{"text": "Hello"}]}},
        )
        assert result == {"id": "test", "name": "test"}

    def test_stream(self):
        client = _mock_client()
        raw_response = MagicMock()
        client.request.return_value = raw_response
        msgs = Messages(client, WS)
        result = msgs.stream("agent-1", message={"parts": [{"text": "Hello"}]})
        client.request.assert_called_once_with(
            "POST",
            _p("agents", "agent-1", "messages", "stream"),
            json={"message": {"parts": [{"text": "Hello"}]}},
            headers={"accept": "text/event-stream"},
            raw=True,
        )
        assert isinstance(result, Stream)


# ---------------------------------------------------------------------------
# File Attachments
# ---------------------------------------------------------------------------

class TestFileAttachments:
    def test_data_attachment_uses_raw_and_mediaType(self):
        """File data should produce raw + mediaType + metadata.encoding fields."""
        parts = _file_attachments_to_parts([
            FileAttachment(data=b"hello", filename="test.txt", mime_type="text/plain")
        ])
        assert len(parts) == 1
        p = parts[0]
        assert "raw" in p
        assert p["mediaType"] == "text/plain"
        assert p["filename"] == "test.txt"
        assert p["metadata"] == {"encoding": "base64"}
        assert "type" not in p  # no type field
        assert "data" not in p  # renamed to raw
        assert "mime_type" not in p  # renamed to mediaType

    def test_url_attachment_uses_mediaType(self):
        """URL attachment should use mediaType, not mime_type."""
        parts = _file_attachments_to_parts([
            FileAttachment(url="https://example.com/img.png", mime_type="image/png")
        ])
        assert len(parts) == 1
        p = parts[0]
        assert p["url"] == "https://example.com/img.png"
        assert p["mediaType"] == "image/png"
        assert "type" not in p
        assert "mime_type" not in p
        assert "metadata" not in p  # URL refs don't need metadata

    def test_path_attachment(self, tmp_path):
        """File path attachment should produce raw + mediaType + metadata."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        parts = _file_attachments_to_parts([
            FileAttachment(path=str(test_file))
        ])
        assert len(parts) == 1
        p = parts[0]
        assert "raw" in p
        assert p["filename"] == "test.txt"
        assert p["metadata"] == {"encoding": "base64"}
        assert "type" not in p


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

class TestConversations:
    def test_path(self):
        convs = Conversations(_mock_client(), WS)
        assert convs._path("agents", "a1", "conversations") == _p("agents", "a1", "conversations")

    def test_list_returns_cursor_page(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        page = convs.list("agent-1")
        assert isinstance(page, SyncCursorPage)

    def test_create(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.create("agent-1")
        client.post.assert_called_once_with(
            _p("agents", "agent-1", "conversations"),
            json={},
        )

    def test_create_normalizes_contextId(self):
        """Create should normalize contextId to id when no id present."""
        client = _mock_client()
        client.post = MagicMock(return_value={"contextId": "ctx-123"})
        convs = Conversations(client, WS)
        result = convs.create("agent-1")
        assert result["id"] == "ctx-123"
        assert result["contextId"] == "ctx-123"

    def test_get(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.get("agent-1", "conv-1")
        client.get.assert_called_once_with(_p("agents", "agent-1", "conversations", "conv-1"))

    def test_update(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        result = convs.update("agent-1", "conv-1", title="Updated")
        client.patch.assert_called_once_with(
            _p("agents", "agent-1", "conversations", "conv-1"),
            json={"title": "Updated"},
        )

    def test_delete(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        convs.delete("agent-1", "conv-1")
        client.delete.assert_called_once_with(
            _p("agents", "agent-1", "conversations", "conv-1")
        )

    def test_share(self):
        client = _mock_client()
        convs = Conversations(client, WS)
        convs.share("agent-1", "conv-1", public=True)
        client.post.assert_called_once_with(
            _p("agents", "agent-1", "conversations", "conv-1", "share"),
            json={"public": True},
        )


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class TestAnalytics:
    def test_path(self):
        a = Analytics(_mock_client(), WS)
        assert a._path("agents", "a1", "analytics") == _p("agents", "a1", "analytics")

    def test_get_no_params(self):
        client = _mock_client()
        a = Analytics(client, WS)
        result = a.get("agent-1")
        client.get.assert_called_once_with(
            _p("agents", "agent-1", "analytics"),
            params={},
        )

    def test_get_with_params(self):
        client = _mock_client()
        a = Analytics(client, WS)
        result = a.get("agent-1", period="7d", granularity="day")
        client.get.assert_called_once_with(
            _p("agents", "agent-1", "analytics"),
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
            _p("agents", "agent-1", "evaluations"),
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
            _p("agents", "agent-1", "access"),
            json={"userId": "user-1", "role": "reader"},
        )

    def test_revoke(self):
        client = _mock_client()
        acc = Access(client, WS)
        acc.revoke("agent-1", "user", "user-123")
        client.delete.assert_called_once_with(
            _p("agents", "agent-1", "access", "user", "user-123")
        )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class TestTools:
    def test_list(self):
        client = _mock_client()
        tools = Tools(client, WS)
        page = tools.list("agent-1")
        assert isinstance(page, SyncCursorPage)

    def test_list_with_params(self):
        client = _mock_client()
        tools = Tools(client, WS)
        page = tools.list("agent-1", page=2, limit=5)
        assert page._page_size == 5
        assert page._start_page == 2

    def test_create(self):
        client = _mock_client()
        tools = Tools(client, WS)
        result = tools.create("agent-1", name="my-tool", type="function")
        client.post.assert_called_once_with(
            _p("agents", "agent-1", "tools"),
            json={"name": "my-tool", "type": "function"},
        )

    def test_get(self):
        client = _mock_client()
        tools = Tools(client, WS)
        result = tools.get("agent-1", "tool-1")
        client.get.assert_called_once_with(_p("agents", "agent-1", "tools", "tool-1"))

    def test_delete(self):
        client = _mock_client()
        tools = Tools(client, WS)
        tools.delete("agent-1", "tool-1")
        client.delete.assert_called_once_with(_p("agents", "agent-1", "tools", "tool-1"))


# ---------------------------------------------------------------------------
# A2A
# ---------------------------------------------------------------------------

class TestA2A:
    def test_send_uses_jsonrpc(self):
        """A2A send should wrap params in JSON-RPC 2.0 envelope."""
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.send("agent-1", message={"parts": [{"text": "Hello"}]})
        args, kwargs = client.post.call_args
        assert args[0] == _p("agents", "agent-1", "a2a")
        body = kwargs["json"]
        assert body["jsonrpc"] == "2.0"
        assert body["method"] == "tasks/send"
        assert body["params"] == {"message": {"parts": [{"text": "Hello"}]}}
        assert "id" in body

    def test_send_subscribe_uses_jsonrpc(self):
        """A2A sendSubscribe should wrap params in JSON-RPC 2.0 envelope."""
        client = _mock_client()
        raw_response = MagicMock()
        client.request.return_value = raw_response
        a2a = A2A(client, WS)
        result = a2a.send_subscribe("agent-1", message={"parts": [{"text": "Hello"}]})
        args, kwargs = client.request.call_args
        assert args[0] == "POST"
        assert args[1] == _p("agents", "agent-1", "a2a")
        body = kwargs["json"]
        assert body["jsonrpc"] == "2.0"
        assert body["method"] == "tasks/sendSubscribe"
        assert body["params"] == {"message": {"parts": [{"text": "Hello"}]}}
        assert isinstance(result, Stream)

    def test_get_card(self):
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.get_card("agent-1")
        client.get.assert_called_once_with(
            _p("agents", "agent-1", ".well-known", "agent.json")
        )

    def test_get_extended_card(self):
        client = _mock_client()
        a2a = A2A(client, WS)
        result = a2a.get_extended_card("agent-1")
        client.get.assert_called_once_with(
            _p("agents", "agent-1", "extendedAgentCard")
        )
