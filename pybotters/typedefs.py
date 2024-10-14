from __future__ import annotations  # pragma: no cover

from typing import TYPE_CHECKING, Any, Protocol  # pragma: no cover

if TYPE_CHECKING:
    import sys
    from collections.abc import Awaitable, Callable, Coroutine
    from contextlib import AbstractAsyncContextManager

    from _typeshed import StrOrBytesPath as StrOrBytesPath
    from aiohttp.client_ws import ClientResponse, ClientWebSocketResponse

    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

    class RequestContextManager(
        Awaitable[ClientResponse], AbstractAsyncContextManager[ClientResponse], Protocol
    ): ...

    APICredentialsDict: TypeAlias = dict[str, list[str]]
    EncodedAPICredential: TypeAlias = tuple[str, bytes, str]
    EncodedAPICredentialsDict: TypeAlias = dict[str, EncodedAPICredential]

    WsStrHandler = Callable[[str, ClientWebSocketResponse], None]
    WsBytesHandler = Callable[[bytes, ClientWebSocketResponse], None]
    WsJsonHandler = Callable[[Any, ClientWebSocketResponse], None]

    WsHeartBeatHandler = Callable[[ClientWebSocketResponse], Coroutine[Any, Any, None]]
    WsRateLimitHandler = Callable[
        [ClientWebSocketResponse, Awaitable[None]], Awaitable[None]
    ]

    Item: TypeAlias = dict[str, Any]
