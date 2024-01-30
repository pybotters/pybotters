import asyncio

from rich import print

import pybotters


async def main():
    async with pybotters.Client(base_url="https://coincheck.com") as client:
        store = pybotters.CoincheckDataStore()

        await client.ws_connect(
            "wss://ws-api.coincheck.com/",
            send_json={"type": "subscribe", "channel": "btc_jpy-orderbook"},
            hdlr_json=store.onmessage,
        )

        await store.initialize(
            client.get("/api/order_books", params={"pair": "btc_jpy"})
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
