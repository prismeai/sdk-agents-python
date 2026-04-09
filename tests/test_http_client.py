"""Tests for SyncAPIClient: request routing, retry logic, error handling, timeout."""

from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import httpx

from prismeai._client import SyncAPIClient, _extract_error_message, _get_retry_delay, _safe_parse
from prismeai._exceptions import (
    PrismeAIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    ConnectionError as PrismeConnectionError,
    TimeoutError as PrismeTimeoutError,
)
from prismeai._constants import DEFAULT_MAX_RETRIES, INITIAL_RETRY_DELAY, MAX_RETRY_DELAY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(status_code=200, json_body=None, text_body="", content=b"some", reason="OK"):
    """Create a mock httpx.Response."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.is_success = 200 <= status_code < 300
    resp.content = content
    resp.reason_phrase = reason
    resp.headers = httpx.Headers({})
    if json_body is not None:
        resp.json.return_value = json_body
    else:
        resp.json.side_effect = Exception("No JSON")
        resp.text = text_body
    return resp


# ---------------------------------------------------------------------------
# _extract_error_message
# ---------------------------------------------------------------------------

class TestExtractErrorMessage:
    def test_dict_with_message(self):
        assert _extract_error_message({"message": "bad input"}, "fallback") == "bad input"

    def test_dict_with_error_string(self):
        assert _extract_error_message({"error": "unauthorized"}, "fallback") == "unauthorized"

    def test_dict_with_error_dict(self):
        body = {"error": {"message": "inner error"}}
        assert _extract_error_message(body, "fallback") == "inner error"

    def test_dict_with_error_dict_no_message(self):
        body = {"error": {"code": 123}}
        assert _extract_error_message(body, "fallback") == "fallback"

    def test_non_dict(self):
        assert _extract_error_message("string body", "fallback") == "fallback"

    def test_none_body(self):
        assert _extract_error_message(None, "fallback") == "fallback"

    def test_empty_dict(self):
        assert _extract_error_message({}, "fallback") == "fallback"

    def test_dict_message_not_string(self):
        assert _extract_error_message({"message": 123}, "fallback") == "fallback"

    def test_dict_error_not_string_or_dict(self):
        assert _extract_error_message({"error": 42}, "fallback") == "fallback"


# ---------------------------------------------------------------------------
# _get_retry_delay
# ---------------------------------------------------------------------------

class TestGetRetryDelay:
    def test_first_attempt_base_delay(self):
        delay = _get_retry_delay(1)
        # Base is 0.5, jitter adds up to 20%
        assert INITIAL_RETRY_DELAY <= delay <= INITIAL_RETRY_DELAY * 1.2

    def test_second_attempt_exponential(self):
        delay = _get_retry_delay(2)
        base = INITIAL_RETRY_DELAY * 2
        assert base <= delay <= base * 1.2

    def test_large_attempt_capped(self):
        delay = _get_retry_delay(100)
        assert delay <= MAX_RETRY_DELAY

    def test_rate_limit_uses_retry_after(self):
        err = RateLimitError("rate limited", headers={"retry-after": "3"})
        delay = _get_retry_delay(1, err)
        assert delay == 3.0

    def test_rate_limit_retry_after_capped(self):
        err = RateLimitError("rate limited", headers={"retry-after": "999"})
        delay = _get_retry_delay(1, err)
        assert delay == MAX_RETRY_DELAY

    def test_non_rate_limit_error_ignores_retry_after(self):
        err = InternalServerError("server error", headers={"retry-after": "3"})
        delay = _get_retry_delay(1, err)
        # Should use exponential backoff, not retry-after
        assert INITIAL_RETRY_DELAY <= delay <= INITIAL_RETRY_DELAY * 1.2


# ---------------------------------------------------------------------------
# _safe_parse
# ---------------------------------------------------------------------------

class TestSafeParse:
    def test_json_success(self):
        resp = MagicMock()
        resp.json.return_value = {"key": "value"}
        assert _safe_parse(resp) == {"key": "value"}

    def test_json_fails_returns_text(self):
        resp = MagicMock()
        resp.json.side_effect = Exception("bad json")
        resp.text = "plain text"
        assert _safe_parse(resp) == "plain text"

    def test_both_fail_returns_none(self):
        resp = MagicMock()
        resp.json.side_effect = Exception("bad json")
        type(resp).text = PropertyMock(side_effect=Exception("no text"))
        assert _safe_parse(resp) is None


# ---------------------------------------------------------------------------
# SyncAPIClient.__init__ / context manager / close
# ---------------------------------------------------------------------------

class TestSyncAPIClientInit:
    def test_base_url_trailing_slash_stripped(self):
        client = SyncAPIClient(
            base_url="https://api.example.com/v2/",
            headers={"x-api-key": "test"},
        )
        assert client._base_url == "https://api.example.com/v2"
        client.close()

    def test_context_manager(self):
        with SyncAPIClient(
            base_url="https://api.example.com",
            headers={},
        ) as client:
            assert isinstance(client, SyncAPIClient)

    def test_close_calls_httpx_close(self):
        client = SyncAPIClient(
            base_url="https://api.example.com",
            headers={},
        )
        client._client = MagicMock()
        client.close()
        client._client.close.assert_called_once()


# ---------------------------------------------------------------------------
# SyncAPIClient.request - success paths
# ---------------------------------------------------------------------------

class TestSyncAPIClientRequest:
    def _make_client(self, max_retries=0):
        client = SyncAPIClient(
            base_url="https://api.example.com",
            headers={"x-api-key": "test"},
            max_retries=max_retries,
        )
        client._client = MagicMock()
        return client

    def test_get_json_response(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"id": "1"})
        client._client.request.return_value = resp
        result = client.request("GET", "/test")
        assert result == {"id": "1"}

    def test_post_json_response(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"created": True})
        client._client.request.return_value = resp
        result = client.request("POST", "/test", json={"name": "x"})
        assert result == {"created": True}
        client._client.request.assert_called_once_with(
            "POST", "/test", json={"name": "x"}, params=None, headers=None,
        )

    def test_request_with_files(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"uploaded": True})
        client._client.request.return_value = resp
        files = {"file": ("test.txt", b"data", "text/plain")}
        result = client.request("POST", "/upload", files=files)
        assert result == {"uploaded": True}
        client._client.request.assert_called_once_with(
            "POST", "/upload", params=None, files=files, headers=None,
        )

    def test_request_strips_none_params(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"ok": True})
        client._client.request.return_value = resp
        result = client.request("GET", "/test", params={"a": "1", "b": None, "c": "3"})
        client._client.request.assert_called_once_with(
            "GET", "/test", json=None, params={"a": "1", "c": "3"}, headers=None,
        )

    def test_request_raw_mode(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"id": "1"})
        client._client.request.return_value = resp
        result = client.request("GET", "/test", raw=True)
        assert result is resp

    def test_request_empty_content_returns_none(self):
        client = self._make_client()
        resp = _make_response(200)
        resp.content = b""
        client._client.request.return_value = resp
        result = client.request("GET", "/test")
        assert result is None

    def test_request_non_json_returns_text(self):
        client = self._make_client()
        resp = _make_response(200, text_body="plain text response")
        client._client.request.return_value = resp
        result = client.request("GET", "/test")
        assert result == "plain text response"

    def test_request_with_custom_headers(self):
        client = self._make_client()
        resp = _make_response(200, json_body={"ok": True})
        client._client.request.return_value = resp
        result = client.request("GET", "/test", headers={"accept": "text/event-stream"})
        client._client.request.assert_called_once_with(
            "GET", "/test", json=None, params=None, headers={"accept": "text/event-stream"},
        )


# ---------------------------------------------------------------------------
# SyncAPIClient.request - error paths
# ---------------------------------------------------------------------------

class TestSyncAPIClientErrors:
    def _make_client(self, max_retries=0):
        client = SyncAPIClient(
            base_url="https://api.example.com",
            headers={},
            max_retries=max_retries,
        )
        client._client = MagicMock()
        return client

    def test_401_raises_authentication_error(self):
        client = self._make_client()
        resp = _make_response(401, json_body={"message": "unauthorized"}, reason="Unauthorized")
        client._client.request.return_value = resp
        with pytest.raises(AuthenticationError):
            client.request("GET", "/test")

    def test_404_raises_not_found_error(self):
        client = self._make_client()
        resp = _make_response(404, json_body={"message": "not found"}, reason="Not Found")
        client._client.request.return_value = resp
        with pytest.raises(NotFoundError):
            client.request("GET", "/test")

    def test_429_raises_rate_limit_error(self):
        client = self._make_client()
        resp = _make_response(429, json_body={"message": "too many"}, reason="Too Many Requests")
        resp.headers = httpx.Headers({"retry-after": "5"})
        client._client.request.return_value = resp
        with pytest.raises(RateLimitError):
            client.request("GET", "/test")

    def test_500_raises_internal_server_error(self):
        client = self._make_client()
        resp = _make_response(500, json_body={"message": "server error"}, reason="Internal Server Error")
        client._client.request.return_value = resp
        with pytest.raises(InternalServerError):
            client.request("GET", "/test")

    def test_timeout_raises_timeout_error(self):
        client = self._make_client()
        client._client.request.side_effect = httpx.TimeoutException("timed out")
        with pytest.raises(PrismeTimeoutError):
            client.request("GET", "/test")

    def test_connection_error_raises_connection_error(self):
        client = self._make_client()
        client._client.request.side_effect = httpx.ConnectError("connection refused")
        with pytest.raises(PrismeConnectionError):
            client.request("GET", "/test")

    def test_error_with_text_body_fallback(self):
        client = self._make_client()
        resp = _make_response(400, text_body="Bad Request text", reason="Bad Request")
        resp.json.side_effect = Exception("no json")
        resp.text = "Bad Request text"
        client._client.request.return_value = resp
        with pytest.raises(PrismeAIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.status_code == 400

    def test_error_message_from_reason_phrase(self):
        client = self._make_client()
        resp = _make_response(418, text_body="", reason="I'm a teapot")
        resp.json.side_effect = Exception("no json")
        resp.text = ""
        client._client.request.return_value = resp
        with pytest.raises(PrismeAIError) as exc_info:
            client.request("GET", "/test")
        assert "I'm a teapot" in str(exc_info.value)


# ---------------------------------------------------------------------------
# SyncAPIClient.request - retry logic
# ---------------------------------------------------------------------------

class TestSyncAPIClientRetry:
    def _make_client(self, max_retries=2):
        client = SyncAPIClient(
            base_url="https://api.example.com",
            headers={},
            max_retries=max_retries,
        )
        client._client = MagicMock()
        return client

    @patch("prismeai._client.time.sleep")
    def test_retries_on_500(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(500, json_body={"message": "error"}, reason="ISE")
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}
        assert client._client.request.call_count == 2
        mock_sleep.assert_called_once()

    @patch("prismeai._client.time.sleep")
    def test_retries_on_429(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(429, json_body={"message": "rate limited"}, reason="Rate Limited")
        fail_resp.headers = httpx.Headers({"retry-after": "1"})
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}

    @patch("prismeai._client.time.sleep")
    def test_retries_on_502(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(502, json_body={"message": "bad gateway"}, reason="Bad Gateway")
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}

    @patch("prismeai._client.time.sleep")
    def test_retries_on_503(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(503, json_body={"message": "unavailable"}, reason="Service Unavailable")
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}

    @patch("prismeai._client.time.sleep")
    def test_retries_on_504(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(504, json_body={"message": "timeout"}, reason="Gateway Timeout")
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}

    @patch("prismeai._client.time.sleep")
    def test_retries_on_408(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(408, json_body={"message": "request timeout"}, reason="Request Timeout")
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [fail_resp, ok_resp]
        result = client.request("GET", "/test")
        assert result == {"ok": True}

    @patch("prismeai._client.time.sleep")
    def test_no_retry_on_400(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(400, json_body={"message": "bad request"}, reason="Bad Request")
        client._client.request.return_value = fail_resp
        with pytest.raises(PrismeAIError):
            client.request("GET", "/test")
        assert client._client.request.call_count == 1
        mock_sleep.assert_not_called()

    @patch("prismeai._client.time.sleep")
    def test_no_retry_on_401(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(401, json_body={"message": "unauthorized"}, reason="Unauthorized")
        client._client.request.return_value = fail_resp
        with pytest.raises(AuthenticationError):
            client.request("GET", "/test")
        assert client._client.request.call_count == 1

    @patch("prismeai._client.time.sleep")
    def test_exhausted_retries_raises(self, mock_sleep):
        client = self._make_client(max_retries=2)
        fail_resp = _make_response(500, json_body={"message": "error"}, reason="ISE")
        client._client.request.return_value = fail_resp
        with pytest.raises(InternalServerError):
            client.request("GET", "/test")
        # 1 initial + 2 retries = 3
        assert client._client.request.call_count == 3

    @patch("prismeai._client.time.sleep")
    def test_timeout_retries_then_raises(self, mock_sleep):
        client = self._make_client(max_retries=1)
        client._client.request.side_effect = httpx.TimeoutException("timeout")
        with pytest.raises(PrismeTimeoutError):
            client.request("GET", "/test")
        assert client._client.request.call_count == 2

    @patch("prismeai._client.time.sleep")
    def test_connection_retries_then_raises(self, mock_sleep):
        client = self._make_client(max_retries=1)
        client._client.request.side_effect = httpx.ConnectError("refused")
        with pytest.raises(PrismeConnectionError):
            client.request("GET", "/test")
        assert client._client.request.call_count == 2

    @patch("prismeai._client.time.sleep")
    def test_timeout_retry_then_success(self, mock_sleep):
        client = self._make_client(max_retries=2)
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [
            httpx.TimeoutException("timeout"),
            ok_resp,
        ]
        result = client.request("GET", "/test")
        assert result == {"ok": True}
        assert client._client.request.call_count == 2

    @patch("prismeai._client.time.sleep")
    def test_connection_retry_then_success(self, mock_sleep):
        client = self._make_client(max_retries=2)
        ok_resp = _make_response(200, json_body={"ok": True})
        client._client.request.side_effect = [
            httpx.ConnectError("refused"),
            ok_resp,
        ]
        result = client.request("GET", "/test")
        assert result == {"ok": True}
        assert client._client.request.call_count == 2


# ---------------------------------------------------------------------------
# Convenience methods
# ---------------------------------------------------------------------------

class TestConvenienceMethods:
    def _make_client(self):
        client = SyncAPIClient(
            base_url="https://api.example.com",
            headers={},
            max_retries=0,
        )
        client._client = MagicMock()
        resp = _make_response(200, json_body={"ok": True})
        client._client.request.return_value = resp
        return client

    def test_get(self):
        client = self._make_client()
        result = client.get("/test", params={"q": "hello"})
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "GET", "/test", json=None, params={"q": "hello"}, headers=None,
        )

    def test_post(self):
        client = self._make_client()
        result = client.post("/test", json={"name": "x"})
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "POST", "/test", json={"name": "x"}, params=None, headers=None,
        )

    def test_post_with_files(self):
        client = self._make_client()
        files = {"file": ("a.txt", b"data", "text/plain")}
        result = client.post("/test", files=files)
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "POST", "/test", params=None, files=files, headers=None,
        )

    def test_put(self):
        client = self._make_client()
        result = client.put("/test", json={"name": "x"})
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "PUT", "/test", json={"name": "x"}, params=None, headers=None,
        )

    def test_patch(self):
        client = self._make_client()
        result = client.patch("/test", json={"name": "x"})
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "PATCH", "/test", json={"name": "x"}, params=None, headers=None,
        )

    def test_delete(self):
        client = self._make_client()
        result = client.delete("/test", params={"id": "1"})
        assert result == {"ok": True}
        client._client.request.assert_called_once_with(
            "DELETE", "/test", json=None, params={"id": "1"}, headers=None,
        )
