import json
import logging
import os
from typing import Dict, List, Optional, TYPE_CHECKING

from .helpers import BaseAuth
from .exchange_hosts import APIS_TABLE, HTTP_HOSTS, WEBSOCKET_HOSTS

if TYPE_CHECKING:
    from .client_reqrep import ClientRequest
    from .client_ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class Auth(BaseAuth):
    def __init__(
        self,
        apis: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self._apis = apis
        self._exchange_auth: Dict[str, BaseAuth] = {}

        self._load_apis()
        self._set_apis()

    def sign(self, request: "ClientRequest") -> None:
        host = request.url.host
        if host in HTTP_HOSTS:
            apiname = HTTP_HOSTS[host]
            if isinstance(apiname, str):
                self._exchange_auth[apiname].sign(request)
            elif callable(apiname):
                self._exchange_auth[apiname(request)].sign(request)

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        host = ws._response.url.host
        if host in WEBSOCKET_HOSTS:
            await self._exchange_auth[WEBSOCKET_HOSTS[host]].wssign(ws)

    def _load_apis(self) -> None:
        if self._apis is None:
            env_apis = os.getenv("PYBOTTERS_APIS")
            if env_apis and os.path.isfile(env_apis):
                with open(env_apis) as fp:
                    self._apis = json.load(fp)
            else:
                self._apis = {}
        elif isinstance(self._apis, dict):
            self._apis = self._apis
        else:
            logger.warning(
                f"apis must be dict or None, not {self._apis.__class__.__name__}"
            )
            self._apis = {}

    def _set_apis(self) -> None:
        for k in self._apis:
            if k in APIS_TABLE:
                self._exchange_auth[k] = APIS_TABLE[k](*self._apis[k])
