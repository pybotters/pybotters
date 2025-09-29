from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

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


class ParamArg(NamedTuple):
    test_input: Any
    expected: Any


@dataclass
class StoreArg:
    name: str
    data: Any


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="allMids",
                    data={
                        "channel": "allMids",
                        "data": {
                            "mids": {
                                "APE": "4.33245",
                                "ARB": "1.21695",
                            }
                        },
                    },
                ),
                expected=[
                    {"coin": "APE", "px": "4.33245"},
                    {"coin": "ARB", "px": "1.21695"},
                ],
            ),
            id="allMids",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="notification",
                    data={
                        "channel": "notification",
                        "data": {
                            "notification": "<notification>",
                        },
                    },
                ),
                expected=[
                    {"notification": "<notification>"},
                ],
            ),
            id="notification",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="webData2",
                    data={
                        "channel": "webData2",
                        "data": {
                            "clearinghouseState": {
                                "marginSummary": {
                                    "accountValue": "29.78001",
                                    "totalNtlPos": "0.0",
                                    "totalRawUsd": "29.78001",
                                    "totalMarginUsed": "0.0",
                                },
                                "crossMarginSummary": {
                                    "accountValue": "29.78001",
                                    "totalNtlPos": "0.0",
                                    "totalRawUsd": "29.78001",
                                    "totalMarginUsed": "0.0",
                                },
                                "crossMaintenanceMarginUsed": "0.0",
                                "withdrawable": "29.78001",
                                "assetPositions": [],
                                "time": 1733968369395,
                            },
                            "user": "0x0000000000000000000000000000000000000001",
                        },
                    },
                ),
                expected=[
                    {
                        "clearinghouseState": {
                            "marginSummary": {
                                "accountValue": "29.78001",
                                "totalNtlPos": "0.0",
                                "totalRawUsd": "29.78001",
                                "totalMarginUsed": "0.0",
                            },
                            "crossMarginSummary": {
                                "accountValue": "29.78001",
                                "totalNtlPos": "0.0",
                                "totalRawUsd": "29.78001",
                                "totalMarginUsed": "0.0",
                            },
                            "crossMaintenanceMarginUsed": "0.0",
                            "withdrawable": "29.78001",
                            "assetPositions": [],
                            "time": 1733968369395,
                        },
                        "user": "0x0000000000000000000000000000000000000001",
                    },
                ],
            ),
            id="webData2",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="candle",
                    data={
                        "channel": "candle",
                        "data": {
                            "T": 1681924499999,
                            "c": "29258.0",
                            "h": "29309.0",
                            "i": "15m",
                            "l": "29250.0",
                            "n": 189,
                            "o": "29295.0",
                            "s": "BTC",
                            "t": 1681923600000,
                            "v": "0.98639",
                        },
                    },
                ),
                expected=[
                    {
                        "T": 1681924499999,
                        "c": "29258.0",
                        "h": "29309.0",
                        "i": "15m",
                        "l": "29250.0",
                        "n": 189,
                        "o": "29295.0",
                        "s": "BTC",
                        "t": 1681923600000,
                        "v": "0.98639",
                    }
                ],
            ),
            id="candle",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="l2Book",
                    data={
                        "channel": "l2Book",
                        "data": {
                            "coin": "TEST",
                            "time": 1681222254710,
                            "levels": [
                                [
                                    {"px": "19900", "sz": "1", "n": 1},
                                    {"px": "19800", "sz": "2", "n": 2},
                                    {"px": "19700", "sz": "3", "n": 3},
                                ],
                                [
                                    {"px": "20100", "sz": "1", "n": 1},
                                    {"px": "20200", "sz": "2", "n": 2},
                                    {"px": "20300", "sz": "3", "n": 3},
                                ],
                            ],
                        },
                    },
                ),
                expected=[
                    {"coin": "TEST", "side": "B", "px": "19900", "sz": "1", "n": 1},
                    {"coin": "TEST", "side": "B", "px": "19800", "sz": "2", "n": 2},
                    {"coin": "TEST", "side": "B", "px": "19700", "sz": "3", "n": 3},
                    {"coin": "TEST", "side": "A", "px": "20100", "sz": "1", "n": 1},
                    {"coin": "TEST", "side": "A", "px": "20200", "sz": "2", "n": 2},
                    {"coin": "TEST", "side": "A", "px": "20300", "sz": "3", "n": 3},
                ],
            ),
            id="l2Book",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="trades",
                    data={
                        "channel": "trades",
                        "data": [
                            {
                                "coin": "AVAX",
                                "side": "B",
                                "px": "18.435",
                                "sz": "93.53",
                                "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                                "time": 1681222254710,
                                "tid": 118906512037719,
                                "users": [
                                    "0x72d73fea74d7ff40c3e5a70e17f5b1aaf47dfc26",
                                    "0x4b9d7caad51e284a45112395da621b94ec82b03f",
                                ],
                            },
                            {
                                "coin": "@107",
                                "side": "A",
                                "px": "18.620413815",
                                "sz": "43.84",
                                "time": 1735969713869,
                                "hash": "0x2222138cc516e3fe746c0411dd733f02e60086f43205af2ae37c93f6a792430b",
                                "tid": 907359904431134,
                                "users": [
                                    "0x0000000000000000000000000000000000000001",
                                    "0xffffffffffffffffffffffffffffffffffffffff",
                                ],
                            },
                        ],
                    },
                ),
                expected=[
                    {
                        "coin": "AVAX",
                        "side": "B",
                        "px": "18.435",
                        "sz": "93.53",
                        "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                        "time": 1681222254710,
                        "tid": 118906512037719,
                        "users": [
                            "0x72d73fea74d7ff40c3e5a70e17f5b1aaf47dfc26",
                            "0x4b9d7caad51e284a45112395da621b94ec82b03f",
                        ],
                    },
                    {
                        "coin": "@107",
                        "side": "A",
                        "px": "18.620413815",
                        "sz": "43.84",
                        "time": 1735969713869,
                        "hash": "0x2222138cc516e3fe746c0411dd733f02e60086f43205af2ae37c93f6a792430b",
                        "tid": 907359904431134,
                        "users": [
                            "0x0000000000000000000000000000000000000001",
                            "0xffffffffffffffffffffffffffffffffffffffff",
                        ],
                    },
                ],
            ),
            id="trades",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="orderUpdates",
                    data={
                        "channel": "orderUpdates",
                        "data": [
                            {
                                "order": {
                                    "coin": "BTC",
                                    "limitPx": "29792.0",
                                    "oid": 91490942,
                                    "side": "A",
                                    "sz": "0.0",
                                    "timestamp": 1681247412573,
                                },
                                "status": "open",
                                "statusTimestamp": 1750141385054,
                            }
                        ],
                    },
                ),
                expected=[
                    {
                        "coin": "BTC",
                        "limitPx": "29792.0",
                        "oid": 91490942,
                        "side": "A",
                        "sz": "0.0",
                        "timestamp": 1681247412573,
                        "status": "open",
                        "statusTimestamp": 1750141385054,
                    }
                ],
            ),
            id="orderUpdates",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="userEvents",
                    data={
                        "channel": "user",
                        "data": {
                            "fills": [
                                {
                                    "coin": "AVAX",
                                    "px": "18.435",
                                    "sz": "93.53",
                                    "side": "B",
                                    "time": 1681222254710,
                                    "startPosition": "26.86",
                                    "dir": "Open Long",
                                    "closedPnl": "0.0",
                                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                                    "oid": 90542681,
                                    "crossed": False,
                                    "fee": "0.01",
                                    "tid": 118906512037719,
                                    "liquidation": {
                                        "liquidatedUser": "0x0000000000000000000000000000000000000000",
                                        "markPx": "18.435",
                                        "method": "<method>",
                                    },
                                    "feeToken": "USDC",
                                    "builderFee": "0.01",
                                },
                            ],
                            "funding": {
                                "time": 1681222254710,
                                "coin": "ETH",
                                "usdc": "-3.625312",
                                "szi": "49.1477",
                                "fundingRate": "0.0000417",
                            },
                            "liquidation": {
                                "lid": 0,
                                "liquidator": "0x0000000000000000000000000000000000000000",
                                "liquidated_user": "0x0000000000000000000000000000000000000000",
                                "liquidated_ntl_pos": "0.0",
                                "liquidated_account_value": "0.0",
                            },
                            "nonUserCancel": [
                                {
                                    "coin": "AVAX",
                                    "oid": 90542681,
                                }
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "type": "fills",
                        "coin": "AVAX",
                        "px": "18.435",
                        "sz": "93.53",
                        "side": "B",
                        "time": 1681222254710,
                        "startPosition": "26.86",
                        "dir": "Open Long",
                        "closedPnl": "0.0",
                        "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                        "oid": 90542681,
                        "crossed": False,
                        "fee": "0.01",
                        "tid": 118906512037719,
                        "liquidation": {
                            "liquidatedUser": "0x0000000000000000000000000000000000000000",
                            "markPx": "18.435",
                            "method": "<method>",
                        },
                        "feeToken": "USDC",
                        "builderFee": "0.01",
                    },
                    {
                        "type": "funding",
                        "time": 1681222254710,
                        "coin": "ETH",
                        "usdc": "-3.625312",
                        "szi": "49.1477",
                        "fundingRate": "0.0000417",
                    },
                    {
                        "type": "liquidation",
                        "lid": 0,
                        "liquidator": "0x0000000000000000000000000000000000000000",
                        "liquidated_user": "0x0000000000000000000000000000000000000000",
                        "liquidated_ntl_pos": "0.0",
                        "liquidated_account_value": "0.0",
                    },
                    {
                        "type": "nonUserCancel",
                        "coin": "AVAX",
                        "oid": 90542681,
                    },
                ],
            ),
            id="userEvents",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="userFundings",
                    data={
                        "channel": "userFundings",
                        "data": {
                            "isSnapshot": True,
                            "user": "0x0000000000000000000000000000000000000001",
                            "fundings": [
                                {
                                    "time": 1681222254710,
                                    "coin": "ETH",
                                    "usdc": "-3.625312",
                                    "szi": "49.1477",
                                    "fundingRate": "0.0000417",
                                },
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "time": 1681222254710,
                        "coin": "ETH",
                        "usdc": "-3.625312",
                        "szi": "49.1477",
                        "fundingRate": "0.0000417",
                    },
                ],
            ),
            id="userFundings",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="userNonFundingLedgerUpdates",
                    data={
                        "channel": "userNonFundingLedgerUpdates",
                        "data": {
                            "isSnapshot": True,
                            "user": "0x0000000000000000000000000000000000000001",
                            "nonFundingLedgerUpdates": [
                                {
                                    "time": 1681222254710,
                                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                                    "delta": {"type": "<type>", "usdc": "0.0"},
                                }
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "time": 1681222254710,
                        "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                        "delta": {"type": "<type>", "usdc": "0.0"},
                    }
                ],
            ),
            id="userNonFundingLedgerUpdates",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="activeAssetCtx",
                    data={
                        "channel": "activeAssetCtx",
                        "data": {
                            "coin": "BTC",
                            "ctx": {
                                "dayNtlVlm": "1169046.29406",
                                "prevDayPx": "15.322",
                                "markPx": "14.3161",
                                "midPx": "14.314",
                                "funding": "0.0000125",
                                "openInterest": "688.11",
                                "oraclePx": "14.32",
                            },
                        },
                    },
                ),
                expected=[
                    {
                        "coin": "BTC",
                        "dayNtlVlm": "1169046.29406",
                        "prevDayPx": "15.322",
                        "markPx": "14.3161",
                        "midPx": "14.314",
                        "funding": "0.0000125",
                        "openInterest": "688.11",
                        "oraclePx": "14.32",
                    }
                ],
            ),
            id="activeAssetCtx",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="activeAssetData",
                    data={
                        "channel": "activeAssetData",
                        "data": {
                            "user": "0x0000000000000000000000000000000000000001",
                            "coin": "ETH",
                            "leverage": {
                                "type": "cross",
                                "value": 20,
                            },
                            "maxTradeSzs": ["0.0", "0.0"],
                            "availableToTrade": ["0.0", "0.0"],
                        },
                    },
                ),
                expected=[
                    {
                        "user": "0x0000000000000000000000000000000000000001",
                        "coin": "ETH",
                        "leverage": {
                            "type": "cross",
                            "value": 20,
                        },
                        "maxTradeSzs": ["0.0", "0.0"],
                        "availableToTrade": ["0.0", "0.0"],
                    }
                ],
            ),
            id="activeAssetData",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="userTwapSliceFills",
                    data={
                        "channel": "userTwapSliceFills",
                        "data": {
                            "isSnapshot": True,
                            "user": "0x0000000000000000000000000000000000000001",
                            "twapSliceFills": [
                                {
                                    "coin": "AVAX",
                                    "px": "18.435",
                                    "sz": "93.53",
                                    "side": "B",
                                    "time": 1681222254710,
                                    "startPosition": "26.86",
                                    "dir": "Open Long",
                                    "closedPnl": "0.0",
                                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                                    "oid": 90542681,
                                    "crossed": False,
                                    "fee": "0.01",
                                    "tid": 118906512037719,
                                    "liquidation": {
                                        "liquidatedUser": "0x0000000000000000000000000000000000000000",
                                        "markPx": "18.435",
                                        "method": "<method>",
                                    },
                                    "feeToken": "USDC",
                                    "builderFee": "0.01",
                                    "twapId": 3156,
                                },
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "coin": "AVAX",
                        "px": "18.435",
                        "sz": "93.53",
                        "side": "B",
                        "time": 1681222254710,
                        "startPosition": "26.86",
                        "dir": "Open Long",
                        "closedPnl": "0.0",
                        "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                        "oid": 90542681,
                        "crossed": False,
                        "fee": "0.01",
                        "tid": 118906512037719,
                        "liquidation": {
                            "liquidatedUser": "0x0000000000000000000000000000000000000000",
                            "markPx": "18.435",
                            "method": "<method>",
                        },
                        "feeToken": "USDC",
                        "builderFee": "0.01",
                        "twapId": 3156,
                    },
                ],
            ),
            id="userTwapSliceFills",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="userTwapHistory",
                    data={
                        "channel": "userTwapHistory",
                        "data": {
                            "isSnapshot": True,
                            "user": "0x0000000000000000000000000000000000000001",
                            "history": [
                                {
                                    "state": {},
                                    "status": {
                                        "status": "<status>",
                                        "description": "<description>",
                                    },
                                    "time": 1681222254710,
                                },
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "state": {},
                        "status": {
                            "status": "<status>",
                            "description": "<description>",
                        },
                        "time": 1681222254710,
                    },
                ],
            ),
            id="userTwapHistory",
        ),
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="bbo",
                    data={
                        "channel": "bbo",
                        "data": {
                            "coin": "TEST",
                            "time": 1708622398623,
                            "bbo": [
                                {"px": "19900", "sz": "1", "n": 1},
                                {"px": "20100", "sz": "1", "n": 1},
                            ],
                        },
                    },
                ),
                expected=[
                    {
                        "coin": "TEST",
                        "time": 1708622398623,
                        "bbo": [
                            {"px": "19900", "sz": "1", "n": 1},
                            {"px": "20100", "sz": "1", "n": 1},
                        ],
                    },
                ],
            ),
            id="bbo",
        ),
    ],
)
def test_hyperliquid(test_input: StoreArg, expected: object) -> None:
    store = pybotters.HyperliquidDataStore()
    store.onmessage(test_input.data)

    s = store[test_input.name]
    assert s is not None
    assert s.find() == expected


def test_hyperliquid_active_orders() -> None:
    store = pybotters.HyperliquidDataStore()

    # Receive the open order event
    store.onmessage(
        {
            "channel": "orderUpdates",
            "data": [
                {
                    "order": {
                        "coin": "BTC",
                        "limitPx": "29792.0",
                        "oid": 91490942,
                        "side": "A",
                        "sz": "0.0",
                        "timestamp": 1681247412573,
                    },
                    "status": "open",
                    "statusTimestamp": 1750141385054,
                }
            ],
        }
    )

    assert len(store.order_updates) == 1
    assert store.order_updates.get({"coin": "BTC", "oid": 91490942}) == {
        "coin": "BTC",
        "limitPx": "29792.0",
        "oid": 91490942,
        "side": "A",
        "sz": "0.0",
        "timestamp": 1681247412573,
        "status": "open",
        "statusTimestamp": 1750141385054,
    }

    # Receive the filled order event
    store.onmessage(
        {
            "channel": "orderUpdates",
            "data": [
                {
                    "order": {
                        "coin": "BTC",
                        "limitPx": "29792.0",
                        "oid": 91490942,
                        "side": "A",
                        "sz": "0.0",
                        "timestamp": 1681247412573,
                    },
                    "status": "filled",  # FILLED ORDER
                    "statusTimestamp": 1750141385054,
                }
            ],
        }
    )

    assert len(store.order_updates) == 0
    assert store.order_updates.get({"coin": "BTC", "oid": 91490942}) is None


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            *ParamArg(
                test_input=StoreArg(
                    name="execution-events",
                    data={
                        "channel": "execution-events",
                        "id": 583710515,
                        "order_id": 8047158658,
                        "event_time": "2025-08-24T04:52:25.000Z",
                        "funds": {"btc": "0.005", "jpy": "-84628.36"},
                        "pair": "btc_jpy",
                        "rate": "16925672.0",
                        "fee_currency": None,
                        "fee": "0.0",
                        "liquidity": "T",
                        "side": "buy",
                    },
                ),
                expected=[
                    {
                        "channel": "execution-events",
                        "id": 583710515,
                        "order_id": 8047158658,
                        "event_time": "2025-08-24T04:52:25.000Z",
                        "funds": {"btc": "0.005", "jpy": "-84628.36"},
                        "pair": "btc_jpy",
                        "rate": "16925672.0",
                        "fee_currency": None,
                        "fee": "0.0",
                        "liquidity": "T",
                        "side": "buy",
                    }
                ],
            ),
            id="execution-events",
        ),
    ],
)
def test_coincheck_private(test_input: StoreArg, expected: object) -> None:
    store = pybotters.CoincheckPrivateDataStore()

    store.onmessage(test_input.data)

    s = store[test_input.name]
    assert s is not None
    assert s.find() == expected


@pytest_asyncio.fixture
async def server_coincheck_private() -> AsyncGenerator[str]:
    routes = web.RouteTableDef()

    @routes.get("/api/exchange/orders/opens")
    async def assets(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "success": True,
                "orders": [
                    {
                        "id": 8169566829,
                        "order_type": "buy",
                        "rate": "16391712.0",
                        "pair": "btc_jpy",
                        "pending_amount": "0.001",
                        "pending_market_buy_amount": None,
                        "stop_loss_rate": None,
                        "created_at": "2025-09-28T06:26:42.000Z",
                    }
                ],
            }
        )

    app = web.Application()
    app.add_routes(routes)

    async with TestServer(app) as server:
        yield str(server.make_url(URL()))


@pytest.mark.asyncio
async def test_coincheck_private_order_initialize(
    server_coincheck_private: str,
) -> None:
    store = pybotters.CoincheckPrivateDataStore()

    async with pybotters.Client(base_url=server_coincheck_private) as client:
        await store.initialize(client.request("GET", "/api/exchange/orders/opens"))

    assert store.order.find() == [
        {
            "id": 8169566829,
            "order_type": "buy",
            "rate": "16391712.0",
            "pair": "btc_jpy",
            "pending_amount": "0.001",
            "pending_market_buy_amount": None,
            "stop_loss_rate": None,
            "created_at": "2025-09-28T06:26:42.000Z",
        }
    ]


def test_coincheck_private_order() -> None:
    store = pybotters.CoincheckPrivateDataStore()

    # Step 1: Place a new order
    store.order.feed_response(
        {
            "success": True,
            "id": 8173686428,
            "amount": "0.0064",
            "rate": "16998705.0",
            "order_type": "buy",
            "pair": "btc_jpy",
            "created_at": "2025-09-29T14:50:21.000Z",
            "market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "stop_loss_rate": None,
        }
    )

    assert store.order.find() == [
        {
            "success": True,
            "id": 8173686428,
            "amount": "0.0064",
            "rate": "16998705.0",
            "order_type": "buy",
            "pair": "btc_jpy",
            "created_at": "2025-09-29T14:50:21.000Z",
            "market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "stop_loss_rate": None,
            "pending_amount": "0.0064",
            "pending_market_buy_amount": None,
        }
    ]

    # Step 2: Receive a partial fill event
    store.onmessage(
        {
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "PARTIALLY_FILL",
            "order_type": "buy",
            "rate": "16998705.0",
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": "0.0064",
            "market_buy_amount": None,
            "latest_executed_amount": "0.001",
            "latest_executed_market_buy_amount": None,
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "event_time": "2025-09-29T14:50:24.000Z",
        }
    )

    assert store.order.find() == [
        {
            "success": True,
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "PARTIALLY_FILL",
            "order_type": "buy",
            "rate": "16998705.0",
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": "0.0064",
            "market_buy_amount": None,
            "latest_executed_amount": "0.001",
            "latest_executed_market_buy_amount": None,
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "created_at": "2025-09-29T14:50:21.000Z",
            "event_time": "2025-09-29T14:50:24.000Z",
            "pending_amount": "0.0054",
            "pending_market_buy_amount": None,
        }
    ]

    # Step 3: Receive a fill event
    store.onmessage(
        {
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "FILL",
            "order_type": "buy",
            "rate": "16998705.0",
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": "0.0064",
            "market_buy_amount": None,
            "latest_executed_amount": "0.0054",
            "latest_executed_market_buy_amount": None,
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "event_time": "2025-09-29T14:50:27.000Z",
        }
    )

    assert store.order.find() == []


def test_coincheck_private_order_market() -> None:
    store = pybotters.CoincheckPrivateDataStore()

    # Step 1: Place a new order
    store.order.feed_response(
        {
            "success": True,
            "id": 8173686428,
            "amount": None,
            "rate": None,
            "order_type": "market_buy",
            "pair": "btc_jpy",
            "created_at": "2025-09-29T14:50:21.000Z",
            "market_buy_amount": "108792.0",
            "time_in_force": "good_til_cancelled",
            "stop_loss_rate": None,
        }
    )

    assert store.order.find() == [
        {
            "success": True,
            "id": 8173686428,
            "amount": None,
            "rate": None,
            "order_type": "market_buy",
            "pair": "btc_jpy",
            "created_at": "2025-09-29T14:50:21.000Z",
            "market_buy_amount": "108792.0",
            "time_in_force": "good_til_cancelled",
            "stop_loss_rate": None,
            "pending_amount": None,
            "pending_market_buy_amount": "108792.0",
        }
    ]

    # Step 2: Receive a partial fill event
    store.onmessage(
        {
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "PARTIALLY_FILL",
            "order_type": "market_buy",
            "rate": None,
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": None,
            "market_buy_amount": "108792.0",
            "latest_executed_amount": None,
            "latest_executed_market_buy_amount": "16999.0",
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "event_time": "2025-09-29T14:50:24.000Z",
        }
    )

    assert store.order.find() == [
        {
            "success": True,
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "PARTIALLY_FILL",
            "order_type": "market_buy",
            "rate": None,
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": None,
            "market_buy_amount": "108792.0",
            "latest_executed_amount": None,
            "latest_executed_market_buy_amount": "16999.0",
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "created_at": "2025-09-29T14:50:21.000Z",
            "event_time": "2025-09-29T14:50:24.000Z",
            "pending_amount": None,
            "pending_market_buy_amount": "91793.0",
        }
    ]

    # Step 3: Receive a fill event
    store.onmessage(
        {
            "channel": "order-events",
            "id": 8173686428,
            "pair": "btc_jpy",
            "order_event": "FILL",
            "order_type": "market_buy",
            "rate": None,
            "stop_loss_rate": None,
            "maker_fee_rate": "0.0",
            "taker_fee_rate": "0.0",
            "amount": None,
            "market_buy_amount": None,
            "latest_executed_amount": None,
            "latest_executed_market_buy_amount": "91793",
            "expired_type": None,
            "prevented_match_id": None,
            "expired_amount": None,
            "expired_market_buy_amount": None,
            "time_in_force": "good_til_cancelled",
            "event_time": "2025-09-29T14:50:27.000Z",
        }
    )

    assert store.order.find() == []
