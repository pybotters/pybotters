from typing import Any, Callable, Coroutine, Dict, Optional

from aiohttp.client_ws import ClientWebSocketResponse

WsStrHandler = Callable[
    [str, ClientWebSocketResponse], Optional[Coroutine[Any, Any, None]]
]
WsJsonHandler = Callable[
    [Any, ClientWebSocketResponse], Optional[Coroutine[Any, Any, None]]
]
Item = Dict[str, Any]
