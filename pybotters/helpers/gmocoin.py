import asyncio
import logging
from typing import NoReturn

from ..client import Client
from ..ws import WebSocketApp

logger = logging.getLogger(__name__)


class GMOCoinHelper:
    def __init__(
        self,
        client: Client,
    ) -> None:
        self._client = client
        self._url = removeprefix(
            "https://api.coin.z.com/private/v1/ws-auth", self._client._base_url
        )

    async def create_access_token(self) -> str:
        r = await self._client.fetch(
            "POST",
            self._url,
        )

        if isinstance(r.data, dict) and r.data.get("status") == 0:
            token = r.data["data"]
            return token
        else:
            raise GMOCoinResponseError(r.text)

    async def extend_access_token(self, token: str) -> None:
        r = await self._client.fetch(
            "PUT",
            self._url,
            data={"token": token},
        )

        if isinstance(r.data, dict) and r.data.get("status") == 0:
            return
        else:
            raise GMOCoinResponseError(r.text)

    async def manage_ws_token(
        self,
        ws: WebSocketApp,
        token: str,
        delay: float = 1800.0,  # 30 minutes
    ) -> NoReturn:
        while True:
            try:
                await self.extend_access_token(token)
            except GMOCoinResponseError as e1:
                try:
                    token = await self.create_access_token()
                except GMOCoinResponseError as e2:
                    logger.debug(
                        f"GMO Coin access token could not be extended or created: {e1} {e2}"
                    )
                else:
                    ws.url = f"wss://api.coin.z.com/ws/private/v1/{token}"
                    logger.debug("GMO Coin Access Token has been created")
            else:
                logger.debug("GMO Coin Access Token has been extended")

            await asyncio.sleep(delay)


class GMOCoinResponseError(Exception): ...


def removeprefix(self: str, prefix: str, /) -> str:
    return self[len(prefix) :]
