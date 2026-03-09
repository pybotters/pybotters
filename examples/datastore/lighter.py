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
        store = pybotters.LighterDataStore()

        await client.ws_connect(
            "wss://mainnet.zklighter.elliot.ai/stream",
            send_json={"type": "subscribe", "channel": "order_book/0"},
            hdlr_json=store.onmessage,
        )

        while True:
            print(store.order_book.sorted(market_id=0, limit=2))
            await store.order_book.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
