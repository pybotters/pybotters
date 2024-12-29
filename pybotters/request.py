from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp.payload import JsonPayload
from multidict import MultiDict

from .auth import Auth, Hosts

if TYPE_CHECKING:
    from collections.abc import Callable

    from yarl import URL


class ClientRequest(aiohttp.ClientRequest):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        method: str = args[0]
        url: URL = args[1]

        if kwargs["params"]:
            q = MultiDict(url.query)
            url2 = url.with_query(kwargs["params"])
            q.extend(url2.query)
            url = url.with_query(q)
            args = (
                method,
                url,
            )
            kwargs["params"] = None

        self.__dict__["_auth"] = kwargs["auth"]
        if kwargs["auth"] is Auth:
            kwargs["auth"] = None
            if url.host in Hosts.items:
                name_or_dynamic_selector = Hosts.items[url.host].name
                if isinstance(name_or_dynamic_selector, str):
                    api_name = name_or_dynamic_selector
                elif callable(name_or_dynamic_selector):
                    api_name = name_or_dynamic_selector(args, kwargs)
                if api_name in kwargs["session"].__dict__["_apis"]:
                    args = Hosts.items[url.host].func(args, kwargs)
        if url.host in ContentTypeHosts.items:
            ContentTypeHosts.items[url.host](args, kwargs)

        super().__init__(*args, **kwargs)

    async def send(self, *args, **kwargs) -> aiohttp.ClientResponse:
        resp = await super().send(*args, **kwargs)
        resp.__dict__["_auth"] = self.__dict__["_auth"]
        resp.__dict__["_raw_session"] = self._session
        return resp


class ContentType:
    """Content-Type specific request modifications.

    This is intended for editing the Content-Type in public API requests. Editing the Content-Type in private API requests is handled by auth.Auth.
    """

    @staticmethod
    def hyperliquid(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}

        if url.path.startswith("/info") and data:
            kwargs["data"] = JsonPayload(data)

        return args


class ContentTypeHosts:
    # NOTE: yarl.URL.host is also allowed to be None. So, for brevity, relax the type check on the `items` key.
    items: dict[
        str | None, Callable[[tuple[str, URL], dict[str, Any]], tuple[str, URL]]
    ] = {
        "api.hyperliquid.xyz": ContentType.hyperliquid,
        "api.hyperliquid-testnet.xyz": ContentType.hyperliquid,
    }
