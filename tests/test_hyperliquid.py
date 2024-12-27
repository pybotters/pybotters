from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from pybotters.helpers.hyperliquid import (
    construct_l1_action,
    construct_user_signed_action,
    generate_message_types,
    get_timestamp_ms,
    sign_typed_data,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case 0: Mainnet; Ref: test_l1_action_signing_order_matches()
        (
            # test_input: tuple[str, Mapping[str, object], int, bool, str | None]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {
                    "type": "order",
                    "orders": [
                        {
                            "a": 1,
                            "b": True,
                            "p": "100",
                            "s": "100",
                            "r": False,
                            "t": {"limit": {"tif": "Gtc"}},
                        }
                    ],
                    "grouping": "na",
                },
                # nonce
                0,
                # is_mainnet
                True,
                # vault_address
                None,
            ),
            # expected: Mapping[str, object]
            {
                "r": "0xd65369825a9df5d80099e513cce430311d7d26ddf477f5b3a33d2806b100d78e",
                "s": "0x2b54116ff64054968aa237c20ca9ff68000f977c93289157748a3162b6ea940e",
                "v": 28,
            },
        ),
        # Case 1: Testnet; Ref: test_l1_action_signing_order_matches()
        (
            # test_input: tuple[str, Mapping[str, object], int, bool, str | None]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {
                    "type": "order",
                    "orders": [
                        {
                            "a": 1,
                            "b": True,
                            "p": "100",
                            "s": "100",
                            "r": False,
                            "t": {"limit": {"tif": "Gtc"}},
                        }
                    ],
                    "grouping": "na",
                },
                # nonce
                0,
                # is_mainnet
                False,
                # vault_address
                None,
            ),
            # expected: Mapping[str, object]
            {
                "r": "0x82b2ba28e76b3d761093aaded1b1cdad4960b3af30212b343fb2e6cdfa4e3d54",
                "s": "0x6b53878fc99d26047f4d7e8c90eb98955a109f44209163f52d8dc4278cbbd9f5",
                "v": 27,
            },
        ),
        # Case 2: Mainnet with vault_address; Ref: test_l1_action_signing_matches_with_vault()
        (
            # test_input: tuple[str, Mapping[str, object], int, bool, str | None]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {"type": "dummy", "num": 100000000000},
                # nonce
                0,
                # is_mainnet
                True,
                # vault_address
                "0x1719884eb866cb12b2287399b15f7db5e7d775ea",
            ),
            # expected: Mapping[str, object]
            {
                "r": "0x3c548db75e479f8012acf3000ca3a6b05606bc2ec0c29c50c515066a326239",
                "s": "0x4d402be7396ce74fbba3795769cda45aec00dc3125a984f2a9f23177b190da2c",
                "v": 28,
            },
        ),
    ],
)
def test_sign_l1_action(
    test_input: tuple[str, Mapping[str, object], int, bool, str | None],
    expected: Mapping[str, object],
) -> None:
    """Test hyperliquid l1 action signature."""

    # Arrange
    private_key, action, nonce, is_mainnet, vault_address = test_input

    # Act
    domain_data, message_types, message_data = construct_l1_action(
        action, nonce, is_mainnet, vault_address
    )
    signature = sign_typed_data(private_key, domain_data, message_types, message_data)

    # Assert
    assert signature == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case 0: usdSend; Ref: test_sign_usd_transfer_action()
        (
            # test_input: tuple[str, Mapping[str, object]]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {
                    "type": "usdSend",
                    "hyperliquidChain": "Testnet",
                    "destination": "0x5e9ee1089755c3435139848e47e6635505d5a13a",
                    "amount": "1",
                    "time": 1687816341423,
                },
            ),
            # expected: Mapping[str, object]
            {
                "r": "0x637b37dd731507cdd24f46532ca8ba6eec616952c56218baeff04144e4a77073",
                "s": "0x11a6a24900e6e314136d2592e2f8d502cd89b7c15b198e1bee043c9589f9fad7",
                "v": 27,
            },
        ),
        # Case 1: withdraw3; Ref: test_sign_withdraw_from_bridge_action()
        (
            # test_input: tuple[str, Mapping[str, object]]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {
                    "type": "withdraw3",
                    "hyperliquidChain": "Testnet",
                    "destination": "0x5e9ee1089755c3435139848e47e6635505d5a13a",
                    "amount": "1",
                    "time": 1687816341423,
                },
            ),
            # expected: Mapping[str, object]
            {
                "r": "0x8363524c799e90ce9bc41022f7c39b4e9bdba786e5f9c72b20e43e1462c37cf9",
                "s": "0x58b1411a775938b83e29182e8ef74975f9054c8e97ebf5ec2dc8d51bfc893881",
                "v": 28,
            },
        ),
        # Case 2: usdClassTransfer; Original test case
        (
            # test_input: tuple[str, Mapping[str, object]]
            (
                # private_key
                "0x0123456789012345678901234567890123456789012345678901234567890123",
                # action
                {
                    "type": "usdClassTransfer",
                    "hyperliquidChain": "Testnet",
                    "amount": "1",
                    "toPerp": False,
                    "nonce": 1687816341423,
                },
            ),
            # expected: Mapping[str, object]
            {
                "r": "0x8167f4c2abb35a12492e49105af268f41834c56b3b9e2b4f91820f7fc3c2c908",
                "s": "0x63d90edcc3d18f9ed6b4f6a081f4f148eb477a7d3792cc2991ef92b2afe19eee",
                "v": 28,
            },
        ),
    ],
)
def test_sign_user_signed_action(
    test_input: tuple[str, Mapping[str, object]],
    expected: Mapping[str, object],
) -> None:
    """Test hyperliquid user signed action signature."""

    # Arrange
    private_key, action = test_input

    # Act
    domain_data, message_types, message_data = construct_user_signed_action(action)
    signature = sign_typed_data(private_key, domain_data, message_types, message_data)

    # Assert
    assert signature == expected


def test_generate_message_types() -> None:
    """Test generate_message_types()."""

    # Arrange
    message_data: Mapping[str, object] = {
        "type": "dummy3",
        "toPerp": False,
        "nonce": 1687816341423,
        "hyperliquidChain": "Testnet",
        "multiSigActionHash": b"\x88O,2\xbbm\xbd\xd6_`3\xe3/\xb2\x8c\x0c\xb6\xf5\xb3E\xdb\x0fdq\xfd3f\xd8\\\x92R\xc1",
    }

    # Act
    message_types = generate_message_types(message_data)

    # Assert
    assert message_types == {
        "HyperliquidTransaction:Dummy": [
            {"name": "toPerp", "type": "bool"},
            {"name": "nonce", "type": "uint64"},
            {"name": "hyperliquidChain", "type": "string"},
            {"name": "multiSigActionHash", "type": "bytes32"},
        ]
    }


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case 0
        (
            # test_input: Mapping[str, object]
            {"invalid": object()},
            # expected: tuple[type[Exception], str]
            (TypeError, "Unsupported type: <class 'object'>"),
        ),
        # Case 1
        (
            # test_input: Mapping[str, object]
            {"num": 100000000000},
            # expected: tuple[type[Exception], str]
            (ValueError, "Primary type not found: {'num': 100000000000}"),
        ),
    ],
)
def test_generate_message_types_raises(
    test_input: Mapping[str, object],
    expected: tuple[type[Exception], str],
) -> None:
    """Test generate_message_types()."""

    # Arrange
    expected_exception, match_ = expected

    # Act, Assert
    with pytest.raises(expected_exception, match=match_):
        generate_message_types(test_input)


def test_get_timestamp_ms() -> None:
    """Test get_timestamp_ms()."""

    # Arrange
    def interger_length(nonce: int) -> int:
        return len(str(abs(nonce)))

    # Act
    nonce_sec = int(time.time())
    nonce = get_timestamp_ms()

    # Assert
    assert isinstance(nonce, int) and (
        # Check if the length of nonce is 3 more than the length of time.time()
        interger_length(nonce) == interger_length(nonce_sec) + 3
    )
