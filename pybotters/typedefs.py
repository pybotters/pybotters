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


class RequestContextManager(
    Awaitable[ClientResponse], AsyncContextManager[ClientResponse], Protocol
): ...


APICredentialsDict = Dict[str, List[str]]
EncodedAPICredential = Tuple[str, bytes, str]
EncodedAPICredentialsDict = Dict[str, EncodedAPICredential]

WsStrHandler = Callable[[str, ClientWebSocketResponse], None]
WsBytesHandler = Callable[[bytes, ClientWebSocketResponse], None]
WsJsonHandler = Callable[[Any, ClientWebSocketResponse], None]

WsHeartBeatHandler = Callable[[ClientWebSocketResponse], Coroutine[Any, Any, None]]
WsRateLimitHandler = Callable[
    [ClientWebSocketResponse, Awaitable[None]], Awaitable[None]
]

Item = Dict[str, Any]
