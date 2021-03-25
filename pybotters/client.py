import asyncio
from typing import Any, Mapping, Optional

import aiohttp
from aiohttp import hdrs
from aiohttp.client import _RequestContextManager
from aiohttp.typedefs import StrOrURL

from .request import ClientRequest
from .ws import ws_run_forever


class Client:
    def __init__(self, apis={}, **kwargs) -> None:
        self._session = aiohttp.ClientSession(request_class=ClientRequest,**kwargs)
        self._session.__dict__['_apis'] = self._encode_apis(apis)

    async def __aenter__(self) -> 'Client':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def close(self) -> None:
        await self._session.close()

    def request(
        self,
        method: str,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]]=None,
        data: Any=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(method, url, params=params, data=data, **kwargs)

    def get(
        self,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]]=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(hdrs.METH_GET, url, params=params, **kwargs)

    def post(
        self,
        url: StrOrURL,
        *,
        data: Any=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(
        self,
        url: StrOrURL,
        *,
        data: Any=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(
        self,
        url: StrOrURL,
        *,
        data: Any=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(hdrs.METH_DELETE, url, data=data, **kwargs)

    async def ws_connect(
        self,
        url: StrOrURL,
        *,
        send_str: Optional[str]=None,
        send_json: Optional[Any]=None,
        hdlr_str=None,
        hdlr_json=None,
        **kwargs: Any,
    ) -> asyncio.Task:
        event = asyncio.Event()
        task = asyncio.create_task(
            ws_run_forever(
                url,
                self._session,
                event,
                send_str=send_str,
                send_json=send_json,
                hdlr_str=hdlr_str,
                hdlr_json=hdlr_json,
                **kwargs,
            )
        )
        await event.wait()
        return task

    @staticmethod
    def _encode_apis(apis):
        encoded = {}
        for name in apis:
            if len(apis[name]) == 2:
                encoded[name] = [apis[name][0], apis[name][1].encode()]
        return encoded
