import pytest
import pytest_mock
from yarl import URL

import pybotters.auth
from pybotters.request import ClientRequest


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
