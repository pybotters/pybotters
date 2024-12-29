from typing import Any
from unittest.mock import patch

import pytest
import pytest_mock
from aiohttp.payload import JsonPayload
from yarl import URL

import pybotters.auth
from pybotters.request import ClientRequest, ContentTypeHosts


@pytest.mark.asyncio
async def test_request_without_auth(mocker: pytest_mock.MockerFixture):
    m_auth = mocker.MagicMock(side_effect=lambda args, kwargs: args)
    items = {
        "example.com": pybotters.auth.Item("example", m_auth),
    }
    mocker.patch.object(pybotters.auth.Hosts, "items", items)
    m_sesison = mocker.MagicMock()
    m_sesison.__dict__["_apis"] = {}
    req = ClientRequest(
        "GET",
        URL("http://example.com"),
        params={"foo": "bar"},
        session=m_sesison,
        auth=None,
    )

    assert req.url == URL("http://example.com?foo=bar")
    assert not m_auth.called


@pytest.mark.asyncio
async def test_request_with_auth(mocker: pytest_mock.MockerFixture):
    m_auth = mocker.MagicMock(side_effect=lambda args, kwargs: args)
    items = {
        "example.com": pybotters.auth.Item("example", m_auth),
    }
    mocker.patch.object(pybotters.auth.Hosts, "items", items)
    m_sesison = mocker.MagicMock()
    m_sesison.__dict__["_apis"] = {"example": ("key", "secret".encode())}
    req = ClientRequest(
        "GET",
        URL("http://example.com"),
        params={"foo": "bar"},
        session=m_sesison,
        auth=pybotters.auth.Auth,
    )

    assert req.url == URL("http://example.com?foo=bar")
    assert m_auth.called


@pytest.mark.asyncio
async def test_request_with_selector(mocker: pytest_mock.MockerFixture):
    m_auth = mocker.MagicMock(side_effect=lambda args, kwargs: args)
    m_selector = mocker.MagicMock(return_value="example_demo")
    items = {
        "example.com": pybotters.auth.Item(m_selector, m_auth),
    }
    mocker.patch.object(pybotters.auth.Hosts, "items", items)
    m_sesison = mocker.MagicMock()
    m_sesison.__dict__["_apis"] = {"example_demo": ("key", "secret".encode())}
    req = ClientRequest(
        "GET",
        URL("http://example.com"),
        params={"foo": "bar"},
        headers={"x-use-demo": "1"},
        session=m_sesison,
        auth=pybotters.auth.Auth,
    )

    assert req.url == URL("http://example.com?foo=bar")
    assert m_auth.called
    assert m_selector.called


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case 0: not in ContentTypeHosts
        (
            # test_input
            URL("http://not-in-content-type.example.com"),
            # expected
            "foo=bar",  # FormData
        ),
        # Case 1: in ContentTypeHosts
        (
            # test_input
            URL("http://in-content-type.example.com"),
            # expected
            '{"foo": "bar"}',  # JsonPayload
        ),
    ],
)
def test_request_content_type(test_input: URL, expected: str):
    # Arrange
    def application_json(
        args: tuple[str, URL], kwargs: dict[str, Any]
    ) -> tuple[str, URL]:
        kwargs["data"] = JsonPayload(kwargs["data"])
        return args

    with patch.object(
        ContentTypeHosts,
        "items",
        {"in-content-type.example.com": application_json},
    ):
        # Act
        req = ClientRequest(
            "GET", test_input, params=None, headers=None, data={"foo": "bar"}, auth=None
        )

    # Assert
    assert req.body.decode() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case: hyperliquid
        (
            # test_input
            (
                # method
                "POST",
                # url
                URL("http://api.hyperliquid.xyz/info"),
                # data
                {"type": "meta"},
            ),
            # expected
            '{"type": "meta"}',
        ),
        # Case: hyperliquid_testnet
        (
            # test_input
            (
                # method
                "POST",
                # url
                URL("http://api.hyperliquid-testnet.xyz/info"),
                # data
                {"type": "meta"},
            ),
            # expected
            '{"type": "meta"}',
        ),
    ],
)
def test_request_content_type_hosts(test_input: tuple[str, URL, Any], expected: str):
    # Arrange
    method, url, data = test_input

    # Act
    req = ClientRequest(method, url, params=None, headers=None, data=data, auth=None)

    # Assert
    assert req.body.decode() == expected
