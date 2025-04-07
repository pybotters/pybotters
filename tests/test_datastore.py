from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from yarl import URL

import pybotters

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import Any

    from pybotters.typedefs import Item


def test_bitgetv2_positions() -> None:
    """Check the behavior of BitgetV2DataStore.positions."""
    store = pybotters.BitgetV2DataStore()
    ws: Any = object()

    # Initial messages
    message_list = [
        {
            "event": "subscribe",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
        },
        {
            "action": "snapshot",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
            "data": [],
            "ts": 1741850535818,
        },
    ]
    for message in message_list:
        store.onmessage(message, ws)

    assert store.positions.find() == []

    # Open the position
    message = {
        "action": "snapshot",
        "arg": {
            "instType": "USDT-FUTURES",
            "channel": "positions",
            "instId": "default",
        },
        "data": [
            {
                "posId": "1244249778959294501",
                "instId": "XRPUSDT",
                "marginCoin": "USDT",
                "marginSize": "0.67098",
                "marginMode": "crossed",
                "holdSide": "long",
                "posMode": "one_way_mode",
                "total": "3",
                "available": "3",
                "frozen": "0",
                "openPriceAvg": "2.2366",
                "leverage": 10,
                "achievedProfits": "0",
                "unrealizedPL": "0.0009",
                "unrealizedPLR": "0.001341321649",
                "liquidationPrice": "-5.882918946895",
                "keepMarginRate": "0.0040",
                "marginRate": "0.001265633757",
                "autoMargin": "off",
                "breakEvenPrice": "2.238882701621",
                "deductedFee": "0.002818116",
                "totalFee": "",
                "cTime": "1732378185023",
                "uTime": "1741850543856",
            }
        ],
        "ts": 1741850543864,
    }
    store.onmessage(message, ws)

    assert store.positions.find() == [
        {
            "instType": "USDT-FUTURES",
            "posId": "1244249778959294501",
            "instId": "XRPUSDT",
            "marginCoin": "USDT",
            "marginSize": "0.67098",
            "marginMode": "crossed",
            "holdSide": "long",
            "posMode": "one_way_mode",
            "total": "3",
            "available": "3",
            "frozen": "0",
            "openPriceAvg": "2.2366",
            "leverage": 10,
            "achievedProfits": "0",
            "unrealizedPL": "0.0009",
            "unrealizedPLR": "0.001341321649",
            "liquidationPrice": "-5.882918946895",
            "keepMarginRate": "0.0040",
            "marginRate": "0.001265633757",
            "autoMargin": "off",
            "breakEvenPrice": "2.238882701621",
            "deductedFee": "0.002818116",
            "totalFee": "",
            "cTime": "1732378185023",
            "uTime": "1741850543856",
        }
    ]

    # Update the position
    message_list = [
        {
            "action": "snapshot",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
            "data": [
                {
                    "posId": "1244249778959294501",
                    "instId": "XRPUSDT",
                    "marginCoin": "USDT",
                    "marginSize": "0.67098",
                    "marginMode": "crossed",
                    "holdSide": "long",
                    "posMode": "one_way_mode",
                    "total": "3",
                    "available": "3",
                    "frozen": "0",
                    "openPriceAvg": "2.2366",
                    "leverage": 10,
                    "achievedProfits": "0",
                    "unrealizedPL": "0.0018",
                    "unrealizedPLR": "0.002682643298",
                    "liquidationPrice": "-5.872646147358",
                    "keepMarginRate": "0.0040",
                    "marginRate": "0.002529090521",
                    "autoMargin": "off",
                    "breakEvenPrice": "2.238882701621",
                    "deductedFee": "0.002818116",
                    "totalFee": "",
                    "cTime": "1732378185023",
                    "uTime": "1741850552269",
                }
            ],
            "ts": 1741850552278,
        },
        {
            "action": "snapshot",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
            "data": [
                {
                    "posId": "1244249778959294501",
                    "instId": "XRPUSDT",
                    "marginCoin": "USDT",
                    "marginSize": "1.34205",
                    "marginMode": "crossed",
                    "holdSide": "long",
                    "posMode": "one_way_mode",
                    "total": "6",
                    "available": "6",
                    "frozen": "0",
                    "openPriceAvg": "2.23675",
                    "leverage": 10,
                    "achievedProfits": "0",
                    "unrealizedPL": "0.0027",
                    "unrealizedPLR": "0.002011847547",
                    "liquidationPrice": "-1.817393474448",
                    "keepMarginRate": "0.0040",
                    "marginRate": "0.002531712712",
                    "autoMargin": "off",
                    "breakEvenPrice": "2.239032854713",
                    "deductedFee": "0.00563661",
                    "totalFee": "",
                    "cTime": "1732378185023",
                    "uTime": "1741850552397",
                }
            ],
            "ts": 1741850552406,
        },
    ]
    for message in message_list:
        store.onmessage(message, ws)

    assert store.positions.find() == [
        {
            "instType": "USDT-FUTURES",
            "posId": "1244249778959294501",
            "instId": "XRPUSDT",
            "marginCoin": "USDT",
            "marginSize": "1.34205",
            "marginMode": "crossed",
            "holdSide": "long",
            "posMode": "one_way_mode",
            "total": "6",
            "available": "6",
            "frozen": "0",
            "openPriceAvg": "2.23675",
            "leverage": 10,
            "achievedProfits": "0",
            "unrealizedPL": "0.0027",
            "unrealizedPLR": "0.002011847547",
            "liquidationPrice": "-1.817393474448",
            "keepMarginRate": "0.0040",
            "marginRate": "0.002531712712",
            "autoMargin": "off",
            "breakEvenPrice": "2.239032854713",
            "deductedFee": "0.00563661",
            "totalFee": "",
            "cTime": "1732378185023",
            "uTime": "1741850552397",
        }
    ]

    # Close the position
    message_list = [
        {
            "action": "snapshot",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
            "data": [
                {
                    "posId": "1244249778959294501",
                    "instId": "XRPUSDT",
                    "marginCoin": "USDT",
                    "marginSize": "1.34205",
                    "marginMode": "crossed",
                    "holdSide": "long",
                    "posMode": "one_way_mode",
                    "total": "6",
                    "available": "6",
                    "frozen": "0",
                    "openPriceAvg": "2.23675",
                    "leverage": 10,
                    "achievedProfits": "0",
                    "unrealizedPL": "0.0159",
                    "unrealizedPLR": "0.011847546664",
                    "liquidationPrice": "-1.817383354448",
                    "keepMarginRate": "0.0040",
                    "marginRate": "0.002532831507",
                    "autoMargin": "off",
                    "breakEvenPrice": "2.239032854713",
                    "deductedFee": "0.00563661",
                    "totalFee": "",
                    "cTime": "1732378185023",
                    "uTime": "1741850552397",
                }
            ],
            "ts": 1741850567305,
        },
        {
            "action": "snapshot",
            "arg": {
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "instId": "default",
            },
            "data": [],
            "ts": 1741850567434,
        },
    ]
    for message in message_list:
        store.onmessage(message, ws)

    assert store.positions.find() == []


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            # test_input
            (
                # msg
                [
                    {
                        "method": "asset_update",
                        "params": [
                            {
                                "asset": "xrp",
                                "amount_precision": 6,
                                "free_amount": "0.000000",
                                "locked_amount": "0.000000",
                                "onhand_amount": "0.000000",
                                "withdrawing_amount": "0.000000",
                            },
                            {
                                "asset": "jpy",
                                "amount_precision": 4,
                                "free_amount": "1000000.0000",
                                "locked_amount": "0.0000",
                                "onhand_amount": "1000000.0100",
                                "withdrawing_amount": "0.0000",
                            },
                        ],
                    },
                    {
                        "method": "asset_update",
                        "params": [
                            {
                                "asset": "jpy",
                                "amount_precision": 4,
                                "free_amount": "1000000.0000",
                                "locked_amount": "0.0000",
                                "onhand_amount": "1000000.0000",
                                "withdrawing_amount": "0.0000",
                            },
                            {
                                "asset": "xrp",
                                "amount_precision": 6,
                                "free_amount": "0.000100",
                                "locked_amount": "0.000000",
                                "onhand_amount": "0.000100",
                                "withdrawing_amount": "0.000000",
                            },
                        ],
                    },
                ],
                # name
                "asset",
                # query
                {"asset": "xrp"},
            ),
            # expected
            {
                "asset": "xrp",
                "amount_precision": 6,
                "free_amount": "0.000100",
                "locked_amount": "0.000000",
                "onhand_amount": "0.000100",
                "withdrawing_amount": "0.000000",
            },
            id="asset",
        ),
        pytest.param(
            # test_input
            (
                # msg
                [
                    {
                        "method": "spot_trade",
                        "params": [
                            {
                                "amount": "0.0001",
                                "executed_at": 1742545716306,
                                "fee_amount_base": "0.000000",
                                "fee_amount_quote": "0.0000",
                                "fee_occurred_amount_quote": "0.0000",
                                "maker_taker": "taker",
                                "order_id": 44280655864,
                                "pair": "xrp_jpy",
                                "price": "359.003",
                                "position_side": None,
                                "side": "buy",
                                "trade_id": 1396696263,
                                "type": "market",
                                "profit_loss": None,
                                "interest": None,
                            }
                        ],
                    },
                    {
                        "method": "spot_trade",
                        "params": [
                            {
                                "amount": "0.0001",
                                "executed_at": 1742545746457,
                                "fee_amount_base": "0.000000",
                                "fee_amount_quote": "0.0000",
                                "fee_occurred_amount_quote": "0.0000",
                                "maker_taker": "taker",
                                "order_id": 44280665790,
                                "pair": "xrp_jpy",
                                "price": "359.003",
                                "position_side": None,
                                "side": "sell",
                                "trade_id": 1396696377,
                                "type": "market",
                                "profit_loss": None,
                                "interest": None,
                            }
                        ],
                    },
                ],
                # name
                "spot_trade",
                # query
                {"trade_id": 1396696377},
            ),
            # expected
            {
                "amount": "0.0001",
                "executed_at": 1742545746457,
                "fee_amount_base": "0.000000",
                "fee_amount_quote": "0.0000",
                "fee_occurred_amount_quote": "0.0000",
                "maker_taker": "taker",
                "order_id": 44280665790,
                "pair": "xrp_jpy",
                "price": "359.003",
                "position_side": None,
                "side": "sell",
                "trade_id": 1396696377,
                "type": "market",
                "profit_loss": None,
                "interest": None,
            },
            id="spot_trade",
        ),
        pytest.param(
            # test_input
            (
                # msg
                [
                    {
                        "method": "dealer_order_new",
                        "params": [
                            {
                                "order_id": "44280314922",
                                "asset": "xrp",
                                "side": "sell",
                                "price": "352.372",
                                "amount": "0.000100",
                                "ordered_at": 1742544784403,
                            }
                        ],
                    }
                ],
                # name
                "dealer_order",
                # query
                {"order_id": "44280314922"},
            ),
            # expected
            {
                "order_id": "44280314922",
                "asset": "xrp",
                "side": "sell",
                "price": "352.372",
                "amount": "0.000100",
                "ordered_at": 1742544784403,
            },
            id="dealer_order",
        ),
        pytest.param(
            # test_input
            (
                # msg
                [
                    {
                        "method": "margin_position_update",
                        "params": [
                            {
                                "pair": "xrp_jpy",
                                "position_side": "short",
                                "open": "0.0001",
                                "locked": "0.0000",
                                "product": "0.0360",
                                "average_price": "360.007",
                                "unrealized_fee": "0.0000",
                                "unrealized_interest": "0.0000",
                            }
                        ],
                    },
                    {
                        "method": "margin_position_update",
                        "params": [
                            {
                                "pair": "xrp_jpy",
                                "position_side": "short",
                                "open": "0.0000",
                                "locked": "0.0000",
                                "product": "0.0000",
                                "average_price": "0",
                                "unrealized_fee": "0.0000",
                                "unrealized_interest": "0.0000",
                            }
                        ],
                    },
                ],
                # name
                "margin_position",
                # query
                {"pair": "xrp_jpy", "position_side": "short"},
            ),
            # expected
            {
                "pair": "xrp_jpy",
                "position_side": "short",
                "open": "0.0000",
                "locked": "0.0000",
                "product": "0.0000",
                "average_price": "0",
                "unrealized_fee": "0.0000",
                "unrealized_interest": "0.0000",
            },
            id="margin_position",
        ),
    ],
)
def test_bitbank_private_basic_stores(
    test_input: tuple[list[Any], str, Item], expected: Item
) -> None:
    """Tests for bitbankPrivateDataStore other than spot_order."""
    messages, name, query = test_input

    store = pybotters.bitbankPrivateDataStore()
    for msg in messages:
        store.onmessage(msg)

    s = store[name]
    assert s is not None
    assert s.get(query) == expected


def test_bitbank_private_order() -> None:
    """Tests for bitbankPrivateDataStore spot_order only."""
    store = pybotters.bitbankPrivateDataStore()

    msg: Any
    # Create an order
    msg = {
        "method": "spot_order_new",
        "params": [
            {
                "average_price": "0.000",
                "executed_amount": "0.0000",
                "order_id": 44280998810,
                "ordered_at": 1742546617276,
                "pair": "xrp_jpy",
                "price": "359.412",
                "remaining_amount": "0.0002",
                "side": "buy",
                "start_amount": "0.0002",
                "status": "UNFILLED",
                "type": "limit",
                "expire_at": 1758098617276,
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.find() == [
        {
            "average_price": "0.000",
            "executed_amount": "0.0000",
            "order_id": 44280998810,
            "ordered_at": 1742546617276,
            "pair": "xrp_jpy",
            "price": "359.412",
            "remaining_amount": "0.0002",
            "side": "buy",
            "start_amount": "0.0002",
            "status": "UNFILLED",
            "type": "limit",
            "expire_at": 1758098617276,
            "post_only": True,
            "user_cancelable": True,
        }
    ]

    # Create anoter order
    msg = {
        "method": "spot_order_new",
        "params": [
            {
                "average_price": "0.000",
                "executed_amount": "0.0000",
                "order_id": 44280888880,
                "ordered_at": 1742546316395,
                "pair": "xrp_jpy",
                "price": "354.426",
                "remaining_amount": "0.0001",
                "side": "buy",
                "start_amount": "0.0001",
                "status": "UNFILLED",
                "type": "limit",
                "expire_at": 1758098316395,
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.get({"order_id": 44280888880}) == {
        "average_price": "0.000",
        "executed_amount": "0.0000",
        "order_id": 44280888880,
        "ordered_at": 1742546316395,
        "pair": "xrp_jpy",
        "price": "354.426",
        "remaining_amount": "0.0001",
        "side": "buy",
        "start_amount": "0.0001",
        "status": "UNFILLED",
        "type": "limit",
        "expire_at": 1758098316395,
        "post_only": True,
        "user_cancelable": True,
    }

    # Canceled
    msg = {
        "method": "spot_order",
        "params": [
            {
                "average_price": "0.000",
                "canceled_at": 1742546533125,
                "executed_amount": "0.0000",
                "expire_at": 1758098316395,
                "order_id": 44280888880,
                "ordered_at": 1742546316395,
                "pair": "xrp_jpy",
                "price": "354.426",
                "remaining_amount": "0.0001",
                "side": "buy",
                "start_amount": "0.0001",
                "status": "CANCELED_UNFILLED",
                "type": "limit",
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.find() == [
        {
            "average_price": "0.000",
            "executed_amount": "0.0000",
            "order_id": 44280998810,
            "ordered_at": 1742546617276,
            "pair": "xrp_jpy",
            "price": "359.412",
            "remaining_amount": "0.0002",
            "side": "buy",
            "start_amount": "0.0002",
            "status": "UNFILLED",
            "type": "limit",
            "expire_at": 1758098617276,
            "post_only": True,
            "user_cancelable": True,
        }
    ]

    # Create anoter order (for spot_order_invalidation)
    msg = {
        "method": "spot_order_new",
        "params": [
            {
                "average_price": "0.000",
                "executed_amount": "0.0000",
                "order_id": 44280888880,
                "ordered_at": 1742546316395,
                "pair": "xrp_jpy",
                "price": "354.426",
                "remaining_amount": "0.0001",
                "side": "buy",
                "start_amount": "0.0001",
                "status": "UNFILLED",
                "type": "limit",
                "expire_at": 1758098316395,
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.get({"order_id": 44280888880}) == {
        "average_price": "0.000",
        "executed_amount": "0.0000",
        "order_id": 44280888880,
        "ordered_at": 1742546316395,
        "pair": "xrp_jpy",
        "price": "354.426",
        "remaining_amount": "0.0001",
        "side": "buy",
        "start_amount": "0.0001",
        "status": "UNFILLED",
        "type": "limit",
        "expire_at": 1758098316395,
        "post_only": True,
        "user_cancelable": True,
    }

    # spot_order_invalidation
    msg = {"method": "spot_order_invalidation", "params": {"order_id": [44280888880]}}
    store.onmessage(msg)

    assert store.spot_order.find() == [
        {
            "average_price": "0.000",
            "executed_amount": "0.0000",
            "order_id": 44280998810,
            "ordered_at": 1742546617276,
            "pair": "xrp_jpy",
            "price": "359.412",
            "remaining_amount": "0.0002",
            "side": "buy",
            "start_amount": "0.0002",
            "status": "UNFILLED",
            "type": "limit",
            "expire_at": 1758098617276,
            "post_only": True,
            "user_cancelable": True,
        }
    ]

    # Partially filled
    msg = {
        "method": "spot_order",
        "params": [
            {
                "average_price": "359.412",
                "executed_amount": "0.0001",
                "executed_at": 1742546671700,
                "expire_at": 1758098617276,
                "order_id": 44280998810,
                "ordered_at": 1742546617276,
                "pair": "xrp_jpy",
                "price": "359.412",
                "remaining_amount": "0.0001",
                "side": "buy",
                "start_amount": "0.0002",
                "status": "PARTIALLY_FILLED",
                "type": "limit",
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.find() == [
        {
            "average_price": "359.412",
            "executed_amount": "0.0001",
            "executed_at": 1742546671700,
            "expire_at": 1758098617276,
            "order_id": 44280998810,
            "ordered_at": 1742546617276,
            "pair": "xrp_jpy",
            "price": "359.412",
            "remaining_amount": "0.0001",
            "side": "buy",
            "start_amount": "0.0002",
            "status": "PARTIALLY_FILLED",
            "type": "limit",
            "post_only": True,
            "user_cancelable": True,
        }
    ]

    # Fully filled
    msg = {
        "method": "spot_order",
        "params": [
            {
                "average_price": "359.412",
                "executed_amount": "0.0002",
                "executed_at": 1742546671700,
                "expire_at": 1758098617276,
                "order_id": 44280998810,
                "ordered_at": 1742546617276,
                "pair": "xrp_jpy",
                "price": "359.412",
                "remaining_amount": "0.0000",
                "side": "buy",
                "start_amount": "0.0002",
                "status": "FULLY_FILLED",
                "type": "limit",
                "post_only": True,
                "user_cancelable": True,
            }
        ],
    }
    store.onmessage(msg)

    assert store.spot_order.find() == []


@pytest_asyncio.fixture
async def server_bitbank_private_initialize() -> AsyncGenerator[str]:
    routes = web.RouteTableDef()

    @routes.get("/v1/user/assets")
    async def assets(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "success": 1,
                "data": {
                    "assets": [
                        {
                            "asset": "string",
                            "free_amount": "string",
                            "amount_precision": 0,
                            "onhand_amount": "string",
                            "locked_amount": "string",
                            "withdrawing_amount": "string",
                            "withdrawal_fee": {"min": "string", "max": "string"},
                            "stop_deposit": False,
                            "stop_withdrawal": False,
                            "network_list": [
                                {
                                    "asset": "string",
                                    "network": "string",
                                    "stop_deposit": False,
                                    "stop_withdrawal": False,
                                    "withdrawal_fee": "string",
                                }
                            ],
                            "collateral_ratio": "string",
                        },
                        {
                            "asset": "jpy",
                            "free_amount": "string",
                            "amount_precision": 0,
                            "onhand_amount": "string",
                            "locked_amount": "string",
                            "withdrawing_amount": "string",
                            "withdrawal_fee": {
                                "under": "string",
                                "over": "string",
                                "threshold": "string",
                            },
                            "stop_deposit": False,
                            "stop_withdrawal": False,
                            "collateral_ratio": "string",
                        },
                    ]
                },
            }
        )

    @routes.get("/v1/user/spot/active_orders")
    async def spot_orders(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "success": 1,
                "data": {
                    "orders": [
                        {
                            "order_id": 0,
                            "pair": "string",
                            "side": "string",
                            "position_side": "string",
                            "type": "string",
                            "start_amount": "string",
                            "remaining_amount": "string",
                            "executed_amount": "string",
                            "price": "string",
                            "post_only": False,
                            "user_cancelable": True,
                            "average_price": "string",
                            "ordered_at": 0,
                            "expire_at": 0,
                            "triggered_at": 0,
                            "trigger_price": "string",
                            "status": "string",
                        }
                    ]
                },
            }
        )

    @routes.get("/v1/user/margin/positions")
    async def positions(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "success": 1,
                "data": {
                    "notice": {
                        "what": "string",
                        "occurred_at": 0,
                        "amount": "0",
                        "due_date_at": 0,
                    },
                    "payables": {"amount": "0"},
                    "positions": [
                        {
                            "pair": "string",
                            "position_side": "string",
                            "open_amount": "0",
                            "product": "0",
                            "average_price": "0",
                            "unrealized_fee_amount": "0",
                            "unrealized_interest_amount": "0",
                        }
                    ],
                    "losscut_threshold": {"individual": "0", "company": "0"},
                },
            }
        )

    app = web.Application()
    app.add_routes(routes)

    async with TestServer(app) as server:
        yield str(server.make_url(URL()))


@dataclass
class InputBitbankPrivateInitialize:
    method: str
    url: str
    store_name: str


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            InputBitbankPrivateInitialize("GET", "/v1/user/assets", "asset"),
            [
                {
                    "asset": "string",
                    "free_amount": "string",
                    "amount_precision": 0,
                    "onhand_amount": "string",
                    "locked_amount": "string",
                    "withdrawing_amount": "string",
                    "withdrawal_fee": {"min": "string", "max": "string"},
                    "stop_deposit": False,
                    "stop_withdrawal": False,
                    "network_list": [
                        {
                            "asset": "string",
                            "network": "string",
                            "stop_deposit": False,
                            "stop_withdrawal": False,
                            "withdrawal_fee": "string",
                        }
                    ],
                    "collateral_ratio": "string",
                },
                {
                    "asset": "jpy",
                    "free_amount": "string",
                    "amount_precision": 0,
                    "onhand_amount": "string",
                    "locked_amount": "string",
                    "withdrawing_amount": "string",
                    "withdrawal_fee": {
                        "under": "string",
                        "over": "string",
                        "threshold": "string",
                    },
                    "stop_deposit": False,
                    "stop_withdrawal": False,
                    "collateral_ratio": "string",
                },
            ],
            id="asset",
        ),
        pytest.param(
            InputBitbankPrivateInitialize(
                "GET", "/v1/user/spot/active_orders", "spot_order"
            ),
            [
                {
                    "order_id": 0,
                    "pair": "string",
                    "side": "string",
                    "position_side": "string",
                    "type": "string",
                    "start_amount": "string",
                    "remaining_amount": "string",
                    "executed_amount": "string",
                    "price": "string",
                    "post_only": False,
                    "user_cancelable": True,
                    "average_price": "string",
                    "ordered_at": 0,
                    "expire_at": 0,
                    "triggered_at": 0,
                    "trigger_price": "string",
                    "status": "string",
                }
            ],
            id="spot_order",
        ),
        pytest.param(
            InputBitbankPrivateInitialize(
                "GET", "/v1/user/margin/positions", "margin_position"
            ),
            [
                {
                    "pair": "string",
                    "position_side": "string",
                    "open_amount": "0",
                    "product": "0",
                    "average_price": "0",
                    "unrealized_fee_amount": "0",
                    "unrealized_interest_amount": "0",
                }
            ],
            id="margin_position",
        ),
    ],
)
async def test_bitbank_private_initialize(
    server_bitbank_private_initialize: str,
    test_input: InputBitbankPrivateInitialize,
    expected: list[Item],
) -> None:
    store = pybotters.bitbankPrivateDataStore()

    async with pybotters.Client(base_url=server_bitbank_private_initialize) as client:
        await store.initialize(client.request(test_input.method, test_input.url))

    s = store[test_input.store_name]
    assert s is not None
    assert s.find() == expected
