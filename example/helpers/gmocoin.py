import asyncio
import os

try:
    from rich import print
except ImportError:
    pass

import pybotters
from pybotters.helpers import GMOCoinHelper


async def main():
    apis = {
        "gmocoin": [
            os.getenv("GMOCOIN_API_KEY", ""),
            os.getenv("GMOCOIN_API_SECRET", ""),
        ],
    }

    async with pybotters.Client(apis=apis) as client:
        store = pybotters.GMOCoinDataStore()
        gmohelper = GMOCoinHelper(client)

        token = await gmohelper.create_access_token()

        ws = client.ws_connect(
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
    asyncio.run(main())
