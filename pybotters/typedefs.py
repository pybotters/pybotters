from typing import Any, Callable, Coroutine, Optional

from aiohttp.client_ws import ClientWebSocketResponse

WsStrHandler = Callable[
    [str, ClientWebSocketResponse], Optional[Coroutine[Any, Any, None]]
]
WsJsonHandler = Callable[
    [Any, ClientWebSocketResponse], Optional[Coroutine[Any, Any, None]]
]
Item = dict[str, Any]
