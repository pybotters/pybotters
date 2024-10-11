import asyncio

import pybotters

try:
    from rich import print
except ImportError:
    pass


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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
