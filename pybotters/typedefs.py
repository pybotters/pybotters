from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    List,
    Protocol,
    Tuple,
)

from aiohttp.client_ws import ClientResponse, ClientWebSocketResponse

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath as StrOrBytesPath

    APICredentialsDict = Dict[str, List[str]]
    EncodedAPICredential = Tuple[str, bytes, str]
    EncodedAPICredentialsDict = Dict[str, EncodedAPICredential]

    class RequestContextManager(
        Awaitable[ClientResponse],
        AsyncContextManager[ClientResponse],
        Protocol,
    ): ...

    WsHeartBeatHandler = Callable[[ClientWebSocketResponse], Coroutine[Any, Any, None]]
    WsRateLimitHandler = Callable[
        [ClientWebSocketResponse, Awaitable[None]], Awaitable[None]
    ]


WsStrHandler = Callable[[str, ClientWebSocketResponse], None]
WsBytesHandler = Callable[[bytes, ClientWebSocketResponse], None]
WsJsonHandler = Callable[[Any, ClientWebSocketResponse], None]

Item = Dict[str, Any]
