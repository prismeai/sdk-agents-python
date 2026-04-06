from __future__ import annotations

from typing import Any, Generic, TypeVar, Iterator, AsyncIterator, Callable, Optional, List

T = TypeVar("T")


class PageResponse(Generic[T]):
    """A single page of results."""

    data: List[T]
    total: Optional[int]
    page: Optional[int]
    limit: Optional[int]
    has_more: Optional[bool]

    def __init__(
        self,
        data: List[T],
        total: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        has_more: Optional[bool] = None,
    ) -> None:
        self.data = data
        self.total = total
        self.page = page
        self.limit = limit
        self.has_more = has_more


def default_extractor(body: Any) -> PageResponse[Any]:
    """Default response extractor for paginated endpoints."""
    if isinstance(body, list):
        return PageResponse(data=body, has_more=False)

    if not isinstance(body, dict):
        return PageResponse(data=[], has_more=False)

    data = body.get("results") or body.get("data") or body.get("items") or body.get("documents") or []
    total = body.get("total")
    page = body.get("page")
    limit = body.get("limit")
    has_more = body.get("hasMore")

    if has_more is None and total is not None and page is not None and limit is not None:
        has_more = page * limit < total

    return PageResponse(data=data, total=total, page=page, limit=limit, has_more=has_more)


class SyncCursorPage(Generic[T]):
    """Synchronous paginator — iterable over individual items across pages."""

    def __init__(
        self,
        client: Any,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        extractor: Optional[Callable[[Any], PageResponse[T]]] = None,
        page_size: int = 20,
        start_page: int = 1,
    ) -> None:
        self._client = client
        self._method = method
        self._path = path
        self._params = params or {}
        self._extractor = extractor or default_extractor
        self._page_size = page_size
        self._start_page = start_page

    def get_page(self, page: Optional[int] = None) -> PageResponse[T]:
        target = page or self._start_page
        params = {**self._params, "page": target, "limit": self._page_size}
        raw = self._client.request(self._method, self._path, params=params)
        return self._extractor(raw)

    def to_list(self) -> List[T]:
        return list(self)

    def __iter__(self) -> Iterator[T]:
        page = self._start_page
        while True:
            result = self.get_page(page)
            yield from result.data
            if len(result.data) < self._page_size or result.has_more is False:
                break
            page += 1


class AsyncCursorPage(Generic[T]):
    """Asynchronous paginator — async iterable over individual items across pages."""

    def __init__(
        self,
        client: Any,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        extractor: Optional[Callable[[Any], PageResponse[T]]] = None,
        page_size: int = 20,
        start_page: int = 1,
    ) -> None:
        self._client = client
        self._method = method
        self._path = path
        self._params = params or {}
        self._extractor = extractor or default_extractor
        self._page_size = page_size
        self._start_page = start_page

    async def get_page(self, page: Optional[int] = None) -> PageResponse[T]:
        target = page or self._start_page
        params = {**self._params, "page": target, "limit": self._page_size}
        raw = await self._client.request(self._method, self._path, params=params)
        return self._extractor(raw)

    async def to_list(self) -> List[T]:
        items: List[T] = []
        async for item in self:
            items.append(item)
        return items

    async def __aiter__(self) -> AsyncIterator[T]:
        page = self._start_page
        while True:
            result = await self.get_page(page)
            for item in result.data:
                yield item
            if len(result.data) < self._page_size or result.has_more is False:
                break
            page += 1
