# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters>=1.10",
# ]
# ///

import asyncio
import contextlib
import os

import pybotters

COINCHECK_API_KEY = os.environ["COINCHECK_API_KEY"]
COINCHECK_API_SECRET = os.environ["COINCHECK_API_SECRET"]


async def main() -> None:
    apis = {
        "coincheck": [COINCHECK_API_KEY, COINCHECK_API_SECRET],
    }
    base_url = "https://coincheck.com"

    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        store = pybotters.CoincheckPrivateDataStore()

        # Connect to WebSocket
        await client.ws_connect(
            "wss://stream.coincheck.com",
            send_json={"type": "subscribe", "channels": ["order-events"]},
            hdlr_json=store.onmessage,
        )

        # Initialize open orders
        await store.initialize(
            client.get("/api/exchange/orders/opens"),
        )

        # Fetch ticker
        r = await client.fetch(
            "GET",
            "/api/ticker",
            params={"pair": "btc_jpy"},
        )
        assert r.data
        ask = r.data["ask"]
        bid = r.data["bid"]
        print(f"ask: {ask}, bid: {bid}")

        # Place new order on the bid side for btc_jpy
        r = await client.fetch(
            "POST",
            "/api/exchange/orders",
            data={
                "pair": "btc_jpy",
                "order_type": "buy",
                "rate": str(bid),
                "amount": "0.001",
            },
        )
        assert r.data

        print(r.data)

        # > [!IMPORTANT]
        # Feed order response
        store.order.feed_response(r.data)

        # Watch for order changes
        with store.order.watch() as stream:
            async for change in stream:
                result = store.order.find()
                if len(result) == 0:
                    print("Executed orders!", change)
                    break


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
