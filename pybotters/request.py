from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
from multidict import MultiDict

from .auth import Auth, Hosts

if TYPE_CHECKING:
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

        super().__init__(*args, **kwargs)

    async def send(self, *args, **kwargs) -> aiohttp.ClientResponse:
        resp = await super().send(*args, **kwargs)
        resp.__dict__["_auth"] = self.__dict__["_auth"]
        resp.__dict__["_raw_session"] = self._session
        return resp
