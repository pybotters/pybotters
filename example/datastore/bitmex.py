import asyncio

import pybotters

try:
    from rich import print
except ImportError:
    pass


async def main():
    async with pybotters.Client() as client:
        store = pybotters.BitMEXDataStore()

        await client.ws_connect(
            "wss://ws.bitmex.com/realtime",
            send_json={
                "op": "subscribe",
                "args": ["orderBookL2_25:XBTUSD"],
            },
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
