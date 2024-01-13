from typing import Any, Callable, Dict

from aiohttp.client_ws import ClientWebSocketResponse

WsStrHandler = Callable[[str, ClientWebSocketResponse], None]
WsBytesHandler = Callable[[bytes, ClientWebSocketResponse], None]
WsJsonHandler = Callable[[Any, ClientWebSocketResponse], None]

Item = Dict[str, Any]
