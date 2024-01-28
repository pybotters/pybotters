from __future__ import annotations

import copy
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Literal, Mapping

import aiohttp
from aiohttp import hdrs
from aiohttp.client import _RequestContextManager

from . import __version__
from .auth import Auth
from .request import ClientRequest
from .typedefs import WsBytesHandler, WsJsonHandler, WsStrHandler
from .ws import ClientWebSocketResponse, WebSocketApp

logger = logging.getLogger(__name__)


class Client:
    """
    HTTPリクエストクライアントクラス

    .. note::
        引数 apis は省略できます。

    :Example:

    .. code-block:: python

        async def main():
            async with pybotters.Client(apis={'example': ['KEY', 'SECRET']}) as client:
                r = await client.get('https://...', params={'foo': 'bar'})
                print(await r.json())

    .. code-block:: python

        async def main():
            async with pybotters.Client(apis={'example': ['KEY', 'SECRET']}) as client:
                wstask = await client.ws_connect(
                    'wss://...',
                    send_json={'foo': 'bar'},
                    hdlr_json=print
                    )
                await wstask
                # Ctrl+C to break

    Basic API

    パッケージトップレベルで利用できるHTTPリクエスト関数です。 これらは同期関数です。 内部的にpybotters.Clientをラップしています。

    :Example:

    .. code-block:: python

        r = pybotters.get(
                'https://...',
                params={'foo': 'bar'},
                apis={'example': ['KEY', 'SECRET']}
            )
        print(r.text())
        print(r.json())

    .. code-block:: python

        pybotters.ws_connect(
                'wss://...',
                send_json={'foo': 'bar'},
                hdlr_json=print,
                apis={'example': ['KEY', 'SECRET']}
            )
        # Ctrl+C to break
    """

    _session: aiohttp.ClientSession
    _base_url: str

    def __init__(
        self,
        apis: dict[str, list[str]] | str | None = None,
        base_url: str = "",
        **kwargs: Any,
    ) -> None:
        """
        :param apis: APIキー・シークレットのデータ(optional) ex: {'exchange': ['key', 'secret']}
        :param base_url: リクエストメソッドの url の前方に自動付加するURL(optional)
        :param ``**kwargs``: aiohttp.Client.requestに渡されるキーワード引数(optional)
        """
        self._session = aiohttp.ClientSession(
            request_class=ClientRequest,
            ws_response_class=ClientWebSocketResponse,
            **kwargs,
        )
        if hdrs.USER_AGENT not in self._session.headers:
            self._session.headers[hdrs.USER_AGENT] = f"pybotters/{__version__}"
        apis = self._load_apis(apis)
        self._session.__dict__["_apis"] = self._encode_apis(apis)
        self._base_url = base_url

    async def __aenter__(self) -> "Client":
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
        params: Mapping[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        auth: Auth | None = Auth,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._session.request(
            method=method,
            url=self._base_url + url,
            params=params,
            data=data,
            auth=auth,
            **kwargs,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        data: Any = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        """
        :param method: GET, POST, PUT, DELETE などのHTTPメソッド
        :param url: リクエストURL
        :param params: URLのクエリ文字列(optional)
        :param data: リクエストボディ(optional)
        :param headers: リクエストヘッダー(optional)
        :param auth: API自動認証の機能の有効/無効。デフォルトで有効。auth=Noneを指定することで無効になります(optional)
        :param ``kwargs``: aiohttp.Client.requestに渡されるキーワード引数(optional)
        """
        return self._request(method, url, params=params, data=data, **kwargs)

    async def fetch(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        data: Any = None,
        **kwargs: Any,
    ) -> FetchResult:
        async with self.request(
            method, url, params=params, data=data, **kwargs
        ) as resp:
            text = await resp.text()
            try:
                data = await resp.json(content_type=None)
            except json.JSONDecodeError as e:
                data = NotJSONContent(error=e)

        return FetchResult(response=resp, text=text, data=data)

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_GET, url, params=params, **kwargs)

    def post(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return self._request(hdrs.METH_DELETE, url, data=data, **kwargs)

    def ws_connect(
        self,
        url: str,
        *,
        send_str: str | list[str] | None = None,
        send_bytes: bytes | list[bytes] | None = None,
        send_json: dict | list[dict] | None = None,
        hdlr_str: WsStrHandler | list[WsStrHandler] | None = None,
        hdlr_bytes: WsBytesHandler | list[WsBytesHandler] | None = None,
        hdlr_json: WsJsonHandler | list[WsJsonHandler] | None = None,
        backoff: tuple[float, float, float, float] = WebSocketApp.DEFAULT_BACKOFF,
        heartbeat: float = 10.0,
        auth: Auth | None = Auth,
        **kwargs: Any,
    ) -> WebSocketApp:
        """
        :param url: WebSocket URL
        :param send_str: WebSocketで送信する文字列。文字列、または文字列のリスト形式(optional)
        :param send_json: WebSocketで送信する辞書オブジェクト。辞書、または辞書のリスト形式(optional)
        :param hdlr_str: WebSocketの受信データをハンドリングする関数。
            第1引数 msg に _str_型, 第2引数 ws にWebSocketClientResponse 型の変数が渡されます(optional)
        :param hdlr_json: WebSocketの受信データをハンドリングする関数。
            第1引数 msg に Any 型(JSON-like), 第2引数 ws に WebSocketClientResponse 型の変数が渡されます
            (optional)
        :param headers: リクエストヘッダー(optional)
        :param auth: API自動認証の機能の有効/無効。デフォルトで有効。auth=Noneを指定することで無効になります(optional)
        :param ``**kwargs``: aiohttp.ClientSession.ws_connectに渡されるキーワード引数(optional)
        """
        return WebSocketApp(
            self._session,
            url,
            send_str=send_str,
            send_bytes=send_bytes,
            send_json=send_json,
            hdlr_str=hdlr_str,
            hdlr_bytes=hdlr_bytes,
            hdlr_json=hdlr_json,
            backoff=backoff,
            heartbeat=heartbeat,
            auth=auth,
            **kwargs,
        )

    @staticmethod
    def _load_apis(apis: dict[str, list[str]] | str | None) -> dict[str, list[str]]:
        if apis is None:
            current_apis = os.path.join(os.getcwd(), "apis.json")
            if os.path.isfile(current_apis):
                with open(current_apis) as fp:
                    return json.load(fp)
            else:
                env_apis = os.getenv("PYBOTTERS_APIS")
                if env_apis and os.path.isfile(env_apis):
                    with open(env_apis) as fp:
                        return json.load(fp)
                else:
                    return {}
        elif isinstance(apis, str):
            if os.path.isfile(apis):
                with open(apis) as fp:
                    return json.load(fp)
            else:
                logger.warning(f"No such file or directory: {repr(apis)}")
                return {}
        elif isinstance(apis, dict):
            return copy.deepcopy(apis)
        else:
            logger.warning(f"apis must be dict or str, not {apis.__class__.__name__}")
            return {}

    @staticmethod
    def _encode_apis(apis: dict[str, list[str]]) -> dict[str, tuple[str | bytes, ...]]:
        encoded = {}
        for name in apis:
            if len(apis[name]) >= 2:
                apis[name][1] = apis[name][1].encode()
            encoded[name] = tuple(apis[name])
        return encoded


@dataclass
class FetchResult:
    response: aiohttp.ClientResponse
    text: str
    data: Any | NotJSONContent


@dataclass
class NotJSONContent:
    error: json.JSONDecodeError

    def __bool__(self) -> Literal[False]:
        return False
