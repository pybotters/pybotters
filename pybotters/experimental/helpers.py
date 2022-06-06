import asyncio
import hashlib
import hmac
import inspect
import json
import time
import urllib.parse
from typing import TYPE_CHECKING, Any, Coroutine, Iterable, Optional, Tuple

from aiohttp import BytesPayload, FormData, JsonPayload, hdrs
from aiohttp.typedefs import JSONEncoder
from multidict import CIMultiDict

if TYPE_CHECKING:
    from .client_reqrep import ClientRequest
    from .client_ws import ClientWebSocketResponse


def pretty_description(obj: object) -> str:
    modulename = obj.__class__.__name__
    module = inspect.getmodule(obj)
    if module:
        modulename = f"{module.__name__}.{modulename}"
    return f"{modulename}: {obj}"


def default_json_encoder(
    obj: Any, *, separators: Optional[Tuple[str, str]] = None, **kwargs: Any
):
    if separators is None:
        separators = (",", ":")
    return json.dumps(obj, separators=separators, **kwargs)


DEFAULT_JSON_ENCODER = default_json_encoder


class BaseAuth:
    def __init__(
        self,
        key: Optional[str] = None,
        secret: Optional[str] = None,
        passphrase: Optional[str] = None,
    ) -> None:
        self.key = key or ""
        self.secret = f"{secret or ''}".encode()
        self.passphrase = passphrase or ""

    def sign(self, request: "ClientRequest") -> None:
        return

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        return

    @staticmethod
    async def _wsping(
        coro: Coroutine[Any, Any, None], data: Any, heartbeat: float
    ) -> None:
        while True:
            await asyncio.sleep(heartbeat)
            try:
                await coro(data)
            except ConnectionResetError:
                break

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        return

    @staticmethod
    async def wsratelimit(ws: "ClientWebSocketResponse") -> None:
        return

    def sha256_hexdigest(self, msg: bytes) -> str:
        return hmac.new(self.secret, msg, hashlib.sha256).hexdigest()

    def sha256_digest(self, msg: bytes) -> bytes:
        return hmac.new(self.secret, msg, hashlib.sha256).digest()

    @staticmethod
    def get_seconds(delta_sec: float = 0.0) -> int:
        return int(time.time() + delta_sec)

    @staticmethod
    def get_milliseconds(delta_sec: float = 0.0) -> int:
        return int((time.time() + delta_sec) * 1000)

    @staticmethod
    def to_formdata(
        fields: Iterable[Any] = (),
        quote_fields: bool = True,
        charset: Optional[str] = None,
    ) -> BytesPayload:
        return FormData(fields, quote_fields, charset)()

    @staticmethod
    def to_jsonpayload(
        value: Any,
        encoding: str = "utf-8",
        content_type: str = "application/json",
        dumps: JSONEncoder = json.dumps,
        *args: Any,
        **kwargs: Any,
    ) -> JsonPayload:
        return JsonPayload(value, encoding, content_type, dumps, *args, kwargs)

    @staticmethod
    def urlencode(query, quote=True, *args, **kwargs) -> str:
        if quote:
            return urllib.parse.urlencode(query, *args, **kwargs)
        else:
            return urllib.parse.urlencode(
                query,
                quote_via=lambda string, safe, encoding, errors: string,
                *args,
                **kwargs,
            )

    @staticmethod
    def json_dumps(
        obj,
        *,
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        cls=None,
        indent=None,
        separators=None,
        default=None,
        sort_keys=False,
        **kwargs,
    ) -> str:
        return json.dumps(
            obj,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            cls=cls,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kwargs,
        )

    @staticmethod
    def set_form_urlencoded(headers: CIMultiDict) -> None:
        headers[hdrs.CONTENT_TYPE] = "application/x-www-form-urlencoded"

    @staticmethod
    def set_application_json(headers: CIMultiDict) -> None:
        headers[hdrs.CONTENT_TYPE] = "application/json"

    @staticmethod
    def ishandshake(headers: CIMultiDict) -> bool:
        return headers.get(hdrs.UPGRADE) == "websocket"
