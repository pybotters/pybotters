import asyncio

import pybotters

try:
    from rich import print
except ImportError:
    pass


async def main():
    async with pybotters.Client() as client:
        store = pybotters.PhemexDataStore()

        await client.ws_connect(
            "wss://ws.phemex.com",
            send_json={
                "id": 1234,
                "method": "orderbook_p.subscribe",
                "params": ["BTCUSDT"],
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
