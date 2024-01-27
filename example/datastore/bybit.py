import asyncio

import pybotters
from rich import print


async def main():
    async with pybotters.Client() as client:
        store = pybotters.BybitDataStore()

        await client.ws_connect(
            "wss://stream.bybit.com/v5/public/linear",
            send_json={"op": "subscribe", "args": ["orderbook.50.BTCUSDT"]},
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
