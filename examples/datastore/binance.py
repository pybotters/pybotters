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
    async with pybotters.Client(base_url="https://fapi.binance.com") as client:
        store = pybotters.BinanceUSDSMDataStore()

        await client.ws_connect(
            "wss://fstream.binance.com/stream",
            send_json={
                "method": "SUBSCRIBE",
                "params": ["btcusdt@depth"],
                "id": 1,
            },
            hdlr_json=store.onmessage,
        )

        await store.initialize(
            client.get("/fapi/v1/depth", params={"symbol": "BTCUSDT", "limit": "1000"})
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
