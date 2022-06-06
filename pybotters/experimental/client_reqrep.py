from typing import Any, Optional

import aiohttp
from aiohttp.helpers import reify
from aiohttp.typedefs import JSONEncoder

from .helpers import BaseAuth


class ClientRequest(aiohttp.ClientRequest):
    auth: Optional[BaseAuth] = None

    def __init__(self, *args, **kwargs):
        self.data = kwargs["data"]
        self.json_serialize: JSONEncoder = getattr(kwargs["session"], "json_serialize")
        super().__init__(*args, **kwargs)

    def update_auth(self, auth: Optional[BaseAuth]) -> None:
        """Set custom auth."""
        if auth is None:
            return

        if not isinstance(auth, BaseAuth):
            raise TypeError(
                f"Auth() must be pybotters.Auth or None, not {auth.__class__.__name__}"
            )

        auth.sign(self)

        # Use in ClientWebSocketResponse
        self.auth = auth

    def update_body_from_data(self, body: Any) -> None:
        return super().update_body_from_data(self.data)

    @property
    def request_info(self) -> "ClientRequest":
        return self


class ClientResponse(aiohttp.ClientResponse):
    _request_info: ClientRequest

    @reify
    def request_info(self) -> ClientRequest:
        return self._request_info
