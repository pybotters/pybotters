from __future__ import annotations

import copy
import json
import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

import aiohttp
from aiohttp import hdrs

from .__version__ import __version__
from .auth import Auth, PassphraseRequiredExchanges
from .request import ClientRequest
from .ws import ClientWebSocketResponse, WebSocketApp

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .typedefs import (
        APICredentialsDict,
        EncodedAPICredentialsDict,
        RequestContextManager,
        StrOrBytesPath,
        WsBytesHandler,
        WsJsonHandler,
        WsStrHandler,
    )

logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        apis: APICredentialsDict | StrOrBytesPath | None = None,
        base_url: str = "",
        **kwargs: Any,
    ) -> None:
        """HTTP / WebSocket API Client.

        自動認証を備えた HTTP クライアントです。

        Args:
            apis: API 認証情報
            base_url: ベース URL
            **kwargs: aiohttp.ClientSession にバイパスされる引数
        """
        self._session = aiohttp.ClientSession(
            request_class=ClientRequest,
            ws_response_class=ClientWebSocketResponse,
            **kwargs,
        )
        if hdrs.USER_AGENT not in self._session.headers:
            self._session.headers[hdrs.USER_AGENT] = f"pybotters/{__version__}"
        loaded_apis = self._load_apis(apis)
        self._session.__dict__["_apis"] = self._encode_apis(loaded_apis)
        self._base_url = base_url

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close client session."""
        await self._session.close()

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        auth: type[Auth] | None = Auth,
        **kwargs: Any,
    ) -> RequestContextManager:
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
    ) -> RequestContextManager:
        """HTTP request.

        Args:
            method: HTTP メソッド
            url: リクエスト URL
            params: リクエスト URL のクエリ文字列
            data: リクエストの本文で送信するデータ
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            aiohttp.ClientResponse

        Usage example: :ref:`http-method-api`
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
        """Fetch API.

        Args:
            method: HTTP メソッド
            url: リクエスト URL
            params: リクエスト URL のクエリ文字列
            data: リクエストの本文で送信するデータ
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            FetchResult

        Usage example: :ref:`fetch-api`
        """
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
    ) -> RequestContextManager:
        """HTTP GET request.

        Args:
            url: リクエスト URL
            params: リクエスト URL のクエリ文字列
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            aiohttp.ClientResponse

        Usage example: :ref:`http-method-api`
        """
        return self._request(hdrs.METH_GET, url, params=params, **kwargs)

    def post(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> RequestContextManager:
        """HTTP POST request.

        Args:
            url: リクエスト URL
            data: リクエストの本文で送信するデータ
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            aiohttp.ClientResponse

        Usage example: :ref:`http-method-api`
        """
        return self._request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> RequestContextManager:
        """HTTP PUT request.

        Args:
            url: リクエスト URL
            params: リクエスト URL のクエリ文字列
            data: リクエストの本文で送信するデータ
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            aiohttp.ClientResponse

        Usage example: :ref:`http-method-api`
        """
        return self._request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(
        self,
        url: str,
        *,
        data: Any = None,
        **kwargs: Any,
    ) -> RequestContextManager:
        """HTTP DELETE request.

        Args:
            url: リクエスト URL
            params: リクエスト URL のクエリ文字列
            data: リクエストの本文で送信するデータ
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.request にバイパスされる引数

        Returns:
            aiohttp.ClientResponse

        Usage example: :ref:`http-method-api`
        """
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
        backoff: tuple[float, float, float, float] = WebSocketApp._DEFAULT_BACKOFF,
        autoping: bool = True,
        heartbeat: float = 10.0,
        auth: type[Auth] | None = Auth,
        **kwargs: Any,
    ) -> WebSocketApp:
        """WebSocket request.

        Args:
            url: リクエスト WebSocket URL
            send_str: 送信する WebSocket メッセージ (文字列)
            send_bytes: 送信する WebSocket メッセージ (バイト)
            send_json: 送信する WebSocket メッセージ (JSON)
            hdlr_str: WebSocket メッセージをハンドリングするコールバック (文字列)
            hdlr_bytes: WebSocket メッセージをハンドリングするコールバック (バイト)
            hdlr_json: WebSocket メッセージをハンドリングするコールバック (JSON)
            backoff: 再接続の指数バックオフ (最小、最大、係数、初期値)
            autoping: Ping に対する自動 Pong 応答 (デフォルト True)
            heartbeat: WebSocket ハートビート (デフォルト 10.0 秒)
            auth: 認証オプション (デフォルトで有効、None で無効)
            **kwargs: aiohttp.ClientSession.ws_connect にバイパスされる引数

        Returns:
            WebSocketApp

        Usage example: :ref:`websocket-api`
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
            autoping=autoping,
            heartbeat=heartbeat,
            auth=auth,
            **kwargs,
        )

    @staticmethod
    def _load_apis(
        apis: APICredentialsDict | StrOrBytesPath | None,
    ) -> APICredentialsDict:
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
        elif isinstance(apis, (str, bytes, os.PathLike)):
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
    def _encode_apis(apis: APICredentialsDict) -> EncodedAPICredentialsDict:
        encoded: EncodedAPICredentialsDict = {}
        for name in apis:
            if len(apis[name]) == 2:
                if name in PassphraseRequiredExchanges.items:
                    logger.warning(f"Missing passphrase for {name}")
                    continue
                encoded[name] = (apis[name][0], apis[name][1].encode(), "")
            elif len(apis[name]) == 3:
                encoded[name] = (apis[name][0], apis[name][1].encode(), apis[name][2])
            elif len(apis[name]) == 1:
                encoded[name] = (apis[name][0], b"", "")
        return encoded


@dataclass
class FetchResult:
    """Fetch API result.

    Attributes:
        response: `aiohttp.ClientResponse`
        text: テキストデータ
        data: JSON データ (JSON ではない場合は :class:`.NotJSONContent`)
    """

    response: aiohttp.ClientResponse
    text: str
    data: Any | NotJSONContent


@dataclass
class NotJSONContent:
    """Result of JSON decoding failure.

    Attributes:
        error: `JSONDecodeError`
    """

    error: json.JSONDecodeError

    def __bool__(self) -> Literal[False]:
        return False
