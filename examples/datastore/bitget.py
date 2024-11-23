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
        store = pybotters.BitgetV2DataStore()

        await client.ws_connect(
            "wss://ws.bitget.com/v2/ws/public",
            send_json={
                "op": "subscribe",
                "args": [
                    {
                        "instType": "USDT-FUTURES",
                        "channel": "books",
                        "instId": "BTCUSDT",
                    }
                ],
            },
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.book.sorted(limit=2)
            print(orderbook)

            await store.book.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
