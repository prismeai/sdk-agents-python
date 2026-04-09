"""Tests for APIResponse class and Stream/AsyncStream."""

from unittest.mock import MagicMock
import pytest
import httpx

from prismeai._response import APIResponse
from prismeai._streaming import Stream, SSEDecoder


# ---------------------------------------------------------------------------
# APIResponse
# ---------------------------------------------------------------------------

class TestAPIResponse:
    def _make_http_response(self, status_code=200, headers=None):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = status_code
        resp.headers = httpx.Headers(headers or {})
        return resp

    def test_status_code(self):
        raw = self._make_http_response(201)
        api_resp = APIResponse(raw=raw)
        assert api_resp.status_code == 201

    def test_headers(self):
        raw = self._make_http_response(200, {"content-type": "application/json"})
        api_resp = APIResponse(raw=raw)
        assert api_resp.headers["content-type"] == "application/json"

    def test_parsed_value(self):
        raw = self._make_http_response(200)
        api_resp = APIResponse(raw=raw, parsed={"id": "123"})
        assert api_resp.parsed == {"id": "123"}

    def test_parsed_none_raises_value_error(self):
        raw = self._make_http_response(200)
        api_resp = APIResponse(raw=raw)
        with pytest.raises(ValueError, match="Response has not been parsed"):
            _ = api_resp.parsed

    def test_parsed_with_list(self):
        raw = self._make_http_response(200)
        api_resp = APIResponse(raw=raw, parsed=[1, 2, 3])
        assert api_resp.parsed == [1, 2, 3]

    def test_parsed_with_string(self):
        raw = self._make_http_response(200)
        api_resp = APIResponse(raw=raw, parsed="text result")
        assert api_resp.parsed == "text result"

    def test_http_response_reference(self):
        raw = self._make_http_response(204)
        api_resp = APIResponse(raw=raw)
        assert api_resp.http_response is raw


# ---------------------------------------------------------------------------
# Stream
# ---------------------------------------------------------------------------

class TestStream:
    def test_context_manager(self):
        mock_response = MagicMock()
        stream = Stream(mock_response)
        with stream as s:
            assert s is stream
        mock_response.close.assert_called_once()

    def test_close(self):
        mock_response = MagicMock()
        stream = Stream(mock_response)
        stream.close()
        mock_response.close.assert_called_once()

    def test_iteration(self):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            'data: {"type":"delta","text":"Hello"}',
            "",
            'data: {"type":"delta","text":"World"}',
            "",
            "data: [DONE]",
            "",
        ]
        stream = Stream(mock_response)
        events = list(stream)
        assert len(events) == 2
        assert events[0]["type"] == "delta"
        assert events[0]["text"] == "Hello"
        assert events[1]["type"] == "delta"
        assert events[1]["text"] == "World"

    def test_iteration_skips_done(self):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            "data: [DONE]",
            "",
        ]
        stream = Stream(mock_response)
        events = list(stream)
        assert events == []

    def test_iteration_with_event_type(self):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            "event: message",
            'data: {"text":"Hi"}',
            "",
        ]
        stream = Stream(mock_response)
        events = list(stream)
        assert len(events) == 1
        assert events[0]["__event"] == "message"
        assert events[0]["text"] == "Hi"


# ---------------------------------------------------------------------------
# SSEDecoder - additional coverage beyond test_streaming.py
# ---------------------------------------------------------------------------

class TestSSEDecoderExtra:
    def test_id_and_retry_lines_ignored(self):
        decoder = SSEDecoder()
        events = decoder.feed("id: 123")
        assert events == []
        events = decoder.feed("retry: 5000")
        assert events == []

    def test_non_json_data_returns_data_dict(self):
        decoder = SSEDecoder()
        decoder.feed("data: not-json-data")
        events = decoder.feed("")
        assert len(events) == 1
        assert events[0]["data"] == "not-json-data"

    def test_empty_data_after_collect_returns_none(self):
        decoder = SSEDecoder()
        # Only an event type, no data lines
        decoder.feed("event: ping")
        decoder.feed("data: ")
        events = decoder.feed("")
        # Empty string data = no dispatch (empty string joined => empty)
        # Actually "data: " results in empty string after lstrip
        # The join of [""] is "", which is falsy, so dispatch returns None
        assert events == []

    def test_multiple_events_in_sequence(self):
        decoder = SSEDecoder()
        all_events = []
        for line in [
            'data: {"a":1}', "",
            'data: {"b":2}', "",
        ]:
            all_events.extend(decoder.feed(line))
        assert len(all_events) == 2
        assert all_events[0]["a"] == 1
        assert all_events[1]["b"] == 2

    def test_multiline_json(self):
        decoder = SSEDecoder()
        decoder.feed('data: {"key":')
        decoder.feed('data: "value"}')
        events = decoder.feed("")
        assert len(events) == 1
        # Multiline data joins with \n: '{"key":\n"value"}' which is valid JSON
        assert events[0] == {"key": "value"}

    def test_event_type_reset_after_dispatch(self):
        decoder = SSEDecoder()
        decoder.feed("event: first")
        decoder.feed('data: {"x":1}')
        events1 = decoder.feed("")
        assert events1[0]["__event"] == "first"

        decoder.feed('data: {"y":2}')
        events2 = decoder.feed("")
        assert "__event" not in events2[0]
