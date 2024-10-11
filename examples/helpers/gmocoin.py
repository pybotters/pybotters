# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters",
#     "rich",
# ]
# ///

import asyncio
import os
from contextlib import suppress

import pybotters
from pybotters.helpers import GMOCoinHelper

with suppress(ImportError):
    from rich import print


async def main():
    apis = {
        "gmocoin": [
            os.getenv("GMOCOIN_API_KEY", ""),
            os.getenv("GMOCOIN_API_SECRET", ""),
        ],
    }

    async with pybotters.Client(apis=apis) as client:
        store = pybotters.GMOCoinDataStore()

        # Create a helper instance for GMOCoin.
        gmohelper = GMOCoinHelper(client)

        # Alias for POST /private/v1/ws-auth .
        token = await gmohelper.create_access_token()

        ws = client.ws_connect(
            # Build the Private WebSocket URL.
            f"wss://api.coin.z.com/ws/private/v1/{token}",
            send_json={
                "command": "subscribe",
                "channel": "positionSummaryEvents",
                "option": "PERIODIC",
            },
            hdlr_json=store.onmessage,
        )

        # Create a task to manage WebSocket URL and access token.
        asyncio.create_task(
            gmohelper.manage_ws_token(ws, token),
        )

        with store.position_summary.watch() as stream:
            async for change in stream:
                print(change.data)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
