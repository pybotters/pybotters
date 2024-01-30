import asyncio

import pybotters

try:
    from rich import print
except ImportError:
    pass


async def main():
    async with pybotters.Client() as client:
        store = pybotters.BitgetDataStore()

        await client.ws_connect(
            "wss://ws.bitget.com/mix/v1/stream",
            send_json={
                "op": "subscribe",
                "args": [{"instType": "mc", "channel": "books", "instId": "BTCUSDT"}],
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
