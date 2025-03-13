from __future__ import annotations

from typing import TYPE_CHECKING

import pybotters

if TYPE_CHECKING:
    from typing import Any


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
