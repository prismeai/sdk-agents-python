from unittest.mock import MagicMock
from prismeai._pagination import SyncCursorPage, default_extractor, PageResponse


def test_default_extractor_list():
    result = default_extractor([1, 2, 3])
    assert result.data == [1, 2, 3]
    assert result.has_more is False


def test_default_extractor_results():
    result = default_extractor({"results": [1, 2], "total": 10, "page": 1, "limit": 2})
    assert result.data == [1, 2]
    assert result.total == 10
    assert result.has_more is True


def test_default_extractor_data():
    result = default_extractor({"data": [1, 2], "hasMore": False})
    assert result.data == [1, 2]
    assert result.has_more is False


def test_default_extractor_empty():
    result = default_extractor({})
    assert result.data == []


def test_sync_cursor_page_iteration():
    mock_client = MagicMock()
    mock_client.request.side_effect = [
        {"results": [1, 2], "total": 4, "page": 1, "limit": 2},
        {"results": [3, 4], "total": 4, "page": 2, "limit": 2},
    ]

    page = SyncCursorPage(mock_client, "GET", "/test", page_size=2)
    items = list(page)
    assert items == [1, 2, 3, 4]


def test_sync_cursor_page_to_list():
    mock_client = MagicMock()
    mock_client.request.return_value = {"results": ["a", "b"], "total": 2, "page": 1, "limit": 10}

    page = SyncCursorPage(mock_client, "GET", "/test", page_size=10)
    items = page.to_list()
    assert items == ["a", "b"]


def test_sync_cursor_page_get_page():
    mock_client = MagicMock()
    mock_client.request.return_value = {"results": [3, 4], "total": 4, "page": 2, "limit": 2}

    page = SyncCursorPage(mock_client, "GET", "/test", page_size=2)
    result = page.get_page(2)
    assert result.data == [3, 4]


def test_default_extractor_snake_case_has_more():
    result = default_extractor({"object": "list", "data": [1, 2], "total": 5, "page": 1, "limit": 2, "has_more": False})
    assert result.data == [1, 2]
    assert result.has_more is False


def test_sync_cursor_page_follows_has_more_when_server_caps_limit():
    mock_client = MagicMock()
    mock_client.request.side_effect = [
        {"data": list(range(100)), "total": 150, "page": 1, "limit": 100, "has_more": True},
        {"data": list(range(100, 150)), "total": 150, "page": 2, "limit": 100, "has_more": False},
    ]

    items = SyncCursorPage(mock_client, "GET", "/test", page_size=500).to_list()
    assert items == list(range(150))
    assert [c.kwargs["params"]["page"] for c in mock_client.request.call_args_list] == [1, 2]


def test_sync_cursor_page_stops_on_empty_page():
    mock_client = MagicMock()
    mock_client.request.return_value = {"data": [], "has_more": True}

    assert SyncCursorPage(mock_client, "GET", "/test").to_list() == []
    assert mock_client.request.call_count == 1
