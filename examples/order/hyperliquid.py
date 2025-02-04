# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pybotters>=1.7.0",
#     "rich",
# ]
# ///

import asyncio
import os
from decimal import Decimal
from pprint import pprint

import pybotters

# Your private key: 0x00000...
HYPERLIQUID_TESTNET_PRIVATE_KEY = os.environ["HYPERLIQUID_TESTNET_PRIVATE_KEY"]


def normalize_number(number: str) -> str:
    """Normalize a number.

    e.g. "3300.0" -> "3300"

    Hyperliquid API expects normalized numbers. Otherwise, `L1 error` will occur.
    """
    return format(Decimal(number).normalize(), "f")


async def main() -> None:
    """Place a limit order in Hyperliquid Testnet.

    [!WARNING]
    Please change the private key, target asset, and limit price, etc.
    Default: ETH, buy, 3300, 0.1
    """
    apis = {
        # Mainnet is "hyperliquid"
        "hyperliquid_testnet": [HYPERLIQUID_TESTNET_PRIVATE_KEY],
    }
    base_url = "https://api.hyperliquid-testnet.xyz"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        # Retrieve perpetuals metadata
        # https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-metadata
        r = await client.fetch(
            "POST",
            "/info",
            data={"type": "meta"},
        )
        if not r.data:
            raise r.data.error

        # Construct asset index
        asset_index: dict[str, int] = {
            x["name"]: i for i, x in enumerate(r.data["universe"])
        }
        """e.g.
        {"BTC": 3, "ETH": 4, ...: ...}
        """

        # Place an order
        # https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#place-an-order
        r = await client.fetch(
            "POST",
            "/exchange",
            # [!IMPORTANT]
            # You can omit "nonce" and "signature". They are automatically populated by pybotters 🪄
            data={
                "action": {
                    "type": "order",
                    "orders": [
                        {
                            "a": asset_index["ETH"],  # asset
                            "b": True,  # is_buy
                            "p": normalize_number("3300.0"),  # limit_px
                            "s": normalize_number("0.1"),  # size
                            "r": False,  # reduce_only
                            "t": {"limit": {"tif": "Gtc"}},  # order_type
                        }
                    ],
                    "grouping": "na",
                },
            },
        )
        pprint(r.data)


if __name__ == "__main__":
    asyncio.run(main())
