# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters",
#     "rich",
# ]
# ///

import asyncio
import os
from contextlib import suppress
from dataclasses import dataclass
from typing import Literal

import pybotters

with suppress(ImportError):
    from rich import print


@dataclass
class OrderCondition:
    """Order condition"""

    is_execute: bool
    side: Literal["BUY", "SELL"] | None
    price: float | None
    size: float | None


def your_awesome_algorithm(childorders, positions, board, ticker, executions):
    """Calculate the ordering conditions with your algorithm

    You should do the following:

    1. Calculate limit price, ordrer side and size from board, ticker and executions
    2. Judge whether or not to execute from childorders and positions
    """

    ...

    # Mock algorithm: Buy at best bid - 1000 if there are no existing orders
    price = round(ticker["best_bid"] - 1000.0)
    is_execute = True if not len(childorders) else False

    return OrderCondition(is_execute=is_execute, side="BUY", price=price, size=0.01)


async def main():
    """Main function"""

    product_code = os.getenv("PRODUCT_CODE", "FX_BTC_JPY")

    apis = {
        "bitflyer": [os.getenv("BITFLYER_API_KEY"), os.getenv("BITFLYER_API_SECRET")]
    }
    base_url = "https://api.bitflyer.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        store = pybotters.bitFlyerDataStore()

        print("Initializing DataStore from HTTP ...")
        await store.initialize(
            client.get("/v1/me/getchildorders", params={"product_code": product_code}),
            client.get("/v1/me/getpositions", params={"product_code": product_code}),
        )

        print("Connecting to WebSocket ...")
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "child_order_events"},
                    "id": 1,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": f"lightning_board_snapshot_{product_code}"},
                    "id": 2,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": f"lightning_board_{product_code}"},
                    "id": 3,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": f"lightning_ticker_{product_code}"},
                    "id": 4,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": f"lightning_executions_{product_code}"},
                    "id": 5,
                },
            ],
            hdlr_json=store.onmessage,
        )

        print("Waiting snapshot data from WebSocket ...")
        while not (len(store.board) and len(store.ticker)):
            await store.wait()

        print("Start main loop")
        while True:
            # Retrieve data from DataStore
            childorders = store.childorders.find({"product_code": product_code})
            positions = store.positions.find({"product_code": product_code})
            board = store.board.sorted({"product_code": product_code})
            ticker = store.ticker.get({"product_code": product_code})
            executions = store.executions.find({"product_code": product_code})

            # Calculate the ordering conditions with your algorithm
            condition = your_awesome_algorithm(
                childorders, positions, board, ticker, executions
            )

            print(condition)
            """Example:
            OrderCondition(
                is_execute=True,
                side="BUY",
                price=1234567.0,
                size=0.01,
            )
            """

            if condition.is_execute:
                # Execute order
                with store.childorderevents.watch() as stream:
                    print("Sending order ...")
                    r = await client.fetch(
                        "POST",
                        "/v1/me/sendchildorder",
                        data={
                            "product_code": product_code,
                            "child_order_type": "LIMIT",
                            "side": condition.side,
                            "price": condition.price,
                            "size": condition.size,
                        },
                    )
                    print(f"<Reponse [{r.response.status} {r.response.reason}]>")
                    print(r.data)

                    if r.response.ok and "child_order_acceptance_id" in r.data:
                        print("Waiting for DataStore updates ...")
                        child_order_acceptance_id = r.data["child_order_acceptance_id"]
                        async for change in stream:
                            if (
                                change.data["child_order_acceptance_id"]
                                == child_order_acceptance_id
                            ):
                                break

            print("Waiting for next loop ...")
            await asyncio.sleep(1.0)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
