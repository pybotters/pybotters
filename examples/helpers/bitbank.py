# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters>=1.8",
# ]
# ///

import asyncio
import os
from contextlib import suppress

import pybotters
from pybotters.helpers.bitbank import subscribe_with_callback

BITBANK_API_KEY = os.environ["BITBANK_API_KEY"]
BITBANK_API_SECRET = os.environ["BITBANK_API_SECRET"]


async def main():
    apis = apis = {"bitbank": [BITBANK_API_KEY, BITBANK_API_SECRET]}
    base_url = "https://api.bitbank.cc/v1"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        store = pybotters.bitbankPrivateDataStore()

        await store.initialize(client.get("/user/spot/active_orders"))

        task = asyncio.create_task(subscribe_with_callback(client, store.onmessage))
        try:
            # Example: Watch active orders ...
            with store.spot_order.watch() as stream:
                async for _ in stream:
                    print(store.spot_order.find())
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
