# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters",
#     "rich",
# ]
# ///

import asyncio
from contextlib import suppress

import pybotters

with suppress(ImportError):
    from rich import print


async def main():
    async with pybotters.Client() as client:
        store = pybotters.GMOCoinDataStore()

        await client.ws_connect(
            "wss://api.coin.z.com/ws/public/v1",
            send_json={
                "command": "subscribe",
                "channel": "orderbooks",
                "symbol": "BTC_JPY",
            },
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbooks.sorted(limit=2)
            print(orderbook)

            await store.orderbooks.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
