import asyncio
from typing import Any, Dict, List, Mapping, Optional, Tuple

import aiohttp
from aiohttp import hdrs
from aiohttp.client import _RequestContextManager

from .request import ClientRequest
from .typedefs import WsJsonHandler, WsStrHandler
from .ws import ClientWebSocketResponse, ws_run_forever


class Client:
    _session: aiohttp.ClientSession
    _base_url: str

    def __init__(
        self,
        apis: Dict[str, List[str]]={},
        base_url: str='',
        **kwargs: Any,
    ) -> None:
        self._session = aiohttp.ClientSession(
            request_class=ClientRequest,
            ws_response_class=ClientWebSocketResponse,
            **kwargs,
        )
        self._session.__dict__['_apis'] = self._encode_apis(apis)
        self._base_url = base_url

    async def __aenter__(self) -> 'Client':
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._session.close()
    
    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]]=None,
        data: Optional[Dict[str, Any]]=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(
            method=method,
            url=self._base_url + url,
            params=params,
            data=data,
            **kwargs,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]]=None,
        data: Any=None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._request(method, url, params=params, data=data, **kwargs)

    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, str]]=None,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_GET, url, params=params)

    def post(
        self,
        url: str,
        *,
        data: Any=None,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_POST, url, data=data)

    def put(
        self,
        url: str,
        *,
        data: Any=None,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_PUT, url, data=data)

    def delete(
        self,
        url: str,
        *,
        data: Any=None,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_DELETE, url, data=data)

    async def ws_connect(
        self,
        url: str,
        *,
        send_str: Optional[str]=None,
        send_json: Any=None,
        hdlr_str: Optional[WsStrHandler]=None,
        hdlr_json: Optional[WsJsonHandler]=None,
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
    def _encode_apis(apis: Dict[str, List[str]]) -> Dict[str, Tuple[str, bytes]]:
        encoded = {}
        for name in apis:
            if len(apis[name]) == 2:
                encoded[name] = (apis[name][0], apis[name][1].encode(), )
        return encoded
