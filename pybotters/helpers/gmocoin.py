from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from ..client import Client
    from ..ws import WebSocketApp

logger = logging.getLogger(__name__)


class GMOCoinHelper:
    def __init__(
        self,
        client: Client,
    ) -> None:
        """Post-maintenance reconnection helper for GMO Coin.

        Args:
            client (Client): pybotters.Client
        """
        self._client = client
        self._url = "https://api.coin.z.com/private/v1/ws-auth".removeprefix(
            self._client._base_url
        )

    async def create_access_token(self) -> str:
        """Helper for ``POST /private/v1/ws-auth``.

        Raises:
            GMOCoinResponseError: Response error.

        Returns:
            str: Created access token.
        """
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
        """Helper for ``PUT /private/v1/ws-auth``.

        Args:
            token (str): Access token to extend

        Raises:
            GMOCoinResponseError: Response error.
        """
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
        delay: float = 300.0,  # 5 minutes
    ) -> NoReturn:
        """Manage the access token for the WebSocket connection.

        This method is a coroutine for an infinite loop.
        It should be executed by :meth:`asyncio.create_task`.

        Args:
            ws (WebSocketApp): WebSocketApp instance.
            token (str): Access token.
            delay (float, optional): Sleep time. Defaults to 300.0 (5 minutes).
        """
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
