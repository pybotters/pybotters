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
        store = pybotters.ExtendedDataStore()

        await client.ws_connect(
            "wss://api.starknet.extended.exchange/stream.extended.exchange/v1/orderbooks/BTC-USD",
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
