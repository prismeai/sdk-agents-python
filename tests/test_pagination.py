import asyncio
from copy import deepcopy
from unittest.mock import MagicMock

import httpx
import pytest
import respx

from prismeai import AsyncPrismeAI, PrismeAI
from prismeai._pagination import SyncCursorPage, default_extractor


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


@pytest.mark.parametrize(
    ("total", "page", "limit"),
    [
        (4, 2, 2),
        ("4", 2, 2),
        (4, "2", 2),
        (4, 2, "2"),
        ("4", "2", 2),
        ("4", 2, "2"),
        (4, "2", "2"),
        ("4", "2", "2"),
    ],
)
def test_default_extractor_normalizes_pagination_metadata(total, page, limit):
    body = {"items": [3, 4], "total": total, "page": page, "limit": limit}
    original = deepcopy(body)

    result = default_extractor(body)

    assert result.data == [3, 4]
    assert (result.total, result.page, result.limit) == (4, 2, 2)
    assert all(type(value) is int for value in (result.total, result.page, result.limit))
    assert result.has_more is False
    assert body == original


@pytest.mark.parametrize("body", [{}, {"total": None, "page": None, "limit": None}])
def test_default_extractor_preserves_missing_metadata(body):
    result = default_extractor(body)

    assert (result.total, result.page, result.limit) == (None, None, None)
    assert result.has_more is None


@pytest.mark.parametrize("field", ["total", "page", "limit"])
@pytest.mark.parametrize("value", ["", "invalid", "2.5", "²"])
def test_default_extractor_rejects_invalid_integer_strings(field, value):
    body = {"items": [1], "total": 1, "page": 1, "limit": 1, field: value}

    with pytest.raises(ValueError):
        default_extractor(body)


@pytest.mark.parametrize("flag", ["hasMore", "has_more"])
@pytest.mark.parametrize("has_more", [True, False])
def test_default_extractor_preserves_explicit_pagination_flag(flag, has_more):
    total = 1 if has_more else 2
    result = default_extractor(
        {"items": [1], "total": str(total), "page": "1", "limit": "1", flag: has_more}
    )

    assert result.has_more is has_more
    assert (result.total, result.page, result.limit) == (total, 1, 1)


@pytest.mark.parametrize("async_client", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("page_size", [2, 20], ids=["requested-limit", "server-capped-limit"])
@pytest.mark.parametrize("total", [0, 3, 4], ids=["empty", "partial-last-page", "full-last-page"])
def test_agents_list_paginates_string_metadata(async_client, page_size, total):
    requested_pages = []

    def respond(request):
        page = int(request.url.params["page"])
        requested_pages.append(page)
        assert request.url.params["limit"] == str(page_size)
        assert page <= 2, "Pagination must stop at the reported total"
        items = [{"id": str(i)} for i in range((page - 1) * 2, min(page * 2, total))]
        return httpx.Response(
            200, json={"items": items, "total": total, "page": str(page), "limit": "2"}
        )

    async def collect_async():
        async with AsyncPrismeAI(api_key="test-key", base_url="https://sdk.test") as client:
            return await client.agents.list(limit=page_size).to_list()

    with respx.mock:
        respx.get("https://sdk.test/workspaces/slug:agent-factory/webhooks/v1/agents").mock(
            side_effect=respond
        )
        if async_client:
            items = asyncio.run(collect_async())
        else:
            with PrismeAI(api_key="test-key", base_url="https://sdk.test") as client:
                items = list(client.agents.list(limit=page_size))

    assert items == [{"id": str(i)} for i in range(total)]
    assert requested_pages == ([1] if total == 0 else [1, 2])
