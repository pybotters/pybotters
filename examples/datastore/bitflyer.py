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
        store = pybotters.bitFlyerDataStore()

        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_snapshot_FX_BTC_JPY"},
                    "id": 1,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_FX_BTC_JPY"},
                    "id": 2,
                },
            ],
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.board.sorted(limit=2)
            print(orderbook)

            await store.board.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
