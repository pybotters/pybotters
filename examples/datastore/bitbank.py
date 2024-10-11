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
        store = pybotters.bitbankDataStore()

        await client.ws_connect(
            "wss://stream.bitbank.cc/socket.io/?EIO=3&transport=websocket",
            send_str=[
                '42["join-room","depth_whole_btc_jpy"]',
                '42["join-room","depth_diff_btc_jpy"]',
            ],
            hdlr_str=store.onmessage,
        )

        while True:
            orderbook = store.depth.sorted(limit=2)
            print(orderbook)

            await store.depth.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
