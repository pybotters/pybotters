import logging
from types import TracebackType
from typing import Any, Callable, Dict, List, Mapping, Optional, Type, Union

import aiohttp
import aiohttp.client
from aiohttp import hdrs
from aiohttp.typedefs import JSONEncoder, LooseHeaders, StrOrURL
from yarl import URL

from .client_auth import Auth
from .client_reqrep import ClientRequest, ClientResponse
from .client_ws import ClientWebSocketResponse
from .helpers import BaseAuth, DEFAULT_JSON_ENCODER
from .ws import WebSocketApp

logger = logging.getLogger(__name__)


class Client:
    _base_url: Optional[URL] = None
    _auth: Optional[Union[BaseAuth, Auth]] = None

    def __init__(
        self,
        base_url: Optional[StrOrURL] = None,
        *,
        auth: Optional[BaseAuth] = BaseAuth,
        json_serialize: JSONEncoder = DEFAULT_JSON_ENCODER,
        **kwargs: Any,
    ) -> None:
        if auth is BaseAuth:
            auth = Auth()
        self._auth = auth

        if base_url is not None:
            self._base_url = URL(base_url)

        self._session = aiohttp.ClientSession(
            json_serialize=json_serialize,
            request_class=ClientRequest,
            response_class=ClientResponse,
            ws_response_class=ClientWebSocketResponse,
            **kwargs,
        )

    def request(
        self,
        method: str,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        """Perform HTTP request."""
        return self._request(
            method, url, params=params, data=data, headers=headers, auth=auth, **kwargs
        )

    def _build_url(self, str_or_url: StrOrURL) -> URL:
        url = URL(str_or_url)
        if self._base_url is None:
            return url
        else:
            if self._base_url.path != "/":
                merge_path = self._base_url.path + url.path
            else:
                merge_path = url.path
            return self._base_url.with_path(merge_path).with_query(url.query)

    def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        url = self._build_url(str_or_url)

        if auth is BaseAuth:
            auth = self._auth

        return self._session.request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            **kwargs,
        )

    def ws_connect(
        self,
        url: StrOrURL,
        *,
        send_str: Optional[Union[str, List[str]]] = None,
        send_bytes: Optional[Union[bytes, List[bytes]]] = None,
        send_json: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        receive_str: Optional[Callable[[str, WebSocketApp], None]] = None,
        receive_bytes: Optional[Callable[[bytes, WebSocketApp], None]] = None,
        receive_json: Optional[Callable[[Dict[str, Any], WebSocketApp], None]] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        reconnect: bool = True,
        cooldown_sec: float = 60.0,
        **kwargs: Any,
    ) -> WebSocketApp:
        """Initiate websocket connection."""
        if auth is BaseAuth:
            auth = self._auth

        return WebSocketApp(
            self._session,
            url,
            send_str=send_str,
            send_bytes=send_bytes,
            send_json=send_json,
            receive_str=receive_str,
            receive_bytes=receive_bytes,
            receive_json=receive_json,
            auth=auth,
            reconnect=reconnect,
            cooldown_sec=cooldown_sec,
            **kwargs,
        )

    def get(
        self,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        """Perform HTTP GET request."""
        return self._request(
            hdrs.METH_GET, url, params=params, headers=headers, auth=auth, **kwargs
        )

    def post(
        self,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        """Perform HTTP POST request."""
        return self._request(
            hdrs.METH_POST,
            url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            **kwargs,
        )

    def put(
        self,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        """Perform HTTP PUT request."""
        return self._request(
            hdrs.METH_PUT,
            url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            **kwargs,
        )

    def delete(
        self,
        url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        headers: Optional[LooseHeaders] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        **kwargs: Any,
    ) -> "_RequestContextManager":
        """Perform HTTP DELETE request."""
        return self._request(
            hdrs.METH_DELETE,
            url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            **kwargs,
        )

    async def close(self) -> None:
        """Close underlying connector.

        Release all acquired resources.
        """
        await self._session.close()

    @property
    def closed(self) -> bool:
        """Is client session closed.

        A readonly property.
        """
        return self._session._connector is None or self._session._connector.closed

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()


class _RequestContextManager(aiohttp.client._BaseRequestContextManager[ClientResponse]):
    __slots__ = ()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        # We're basing behavior on the exception as it can be caused by
        # user code unrelated to the status of the connection.  If you
        # would like to close a connection you must do that
        # explicitly.  Otherwise connection error handling should kick in
        # and close/recycle the connection as required.
        self._resp.release()
