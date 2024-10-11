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
    async with pybotters.Client(base_url="https://api-futures.kucoin.com") as client:
        store = pybotters.KuCoinDataStore()

        await store.initialize(client.post("/api/v1/bullet-public"))

        await client.ws_connect(
            store.endpoint,
            send_json={
                "id": 1545910660739,
                "type": "subscribe",
                "topic": "/contractMarket/level2Depth50:XBTUSDTM",
                "privateChannel": False,
                "response": True,
            },
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbook50.sorted(limit=2)
            print(orderbook)

            await store.orderbook50.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
