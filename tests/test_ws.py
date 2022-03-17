import sys
from unittest.mock import MagicMock

import pytest
import pytest_mock
from yarl import URL

import pybotters.auth
import pybotters.ws


def test_heartbeathosts():
    assert hasattr(pybotters.ws.HeartbeatHosts, 'items')
    assert isinstance(pybotters.ws.HeartbeatHosts.items, dict)
    for host, func in pybotters.ws.HeartbeatHosts.items.items():
        assert isinstance(host, str)
        assert callable(func)


def test_wsresponse_without_heartbeat(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.HeartbeatHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://not-example.com')
    m_response.__dict__['_auth'] = None
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert not m_create_task.called


def test_wsresponse_with_heartbeat(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.HeartbeatHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    m_response.__dict__['_auth'] = None
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert m_create_task.called


def test_authhosts():
    assert hasattr(pybotters.ws.AuthHosts, 'items')
    assert isinstance(pybotters.ws.AuthHosts.items, dict)
    for host, item in pybotters.ws.AuthHosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item, pybotters.ws.Item)
        assert isinstance(item.name, str)
        assert callable(item.func)


def test_wsresponse_without_auth(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': pybotters.ws.Item('example', lambda ws: ...),
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.AuthHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    m_response.__dict__['_auth'] = None
    m_session = MagicMock()
    m_session.__dict__['_apis'] = {}
    m_response._session = m_session
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert not m_create_task.called


def test_wsresponse_with_auth(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': pybotters.ws.Item('example', lambda ws: ...),
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.AuthHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    m_response.__dict__['_auth'] = pybotters.auth.Auth
    m_session = MagicMock()
    m_session.__dict__['_apis'] = {'example': ('key', 'secret'.encode())}
    m_response._session = m_session
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert m_create_task.called


@pytest.mark.asyncio
async def test_bitflyer_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    mocker.patch(
        'pybotters.ws.token_hex', return_value='d73b41172d6deca2285e8e58533db082'
    )

    async def dummy_send(msg):
        expected = {
            'method': 'auth',
            'params': {
                'api_key': 'Pcm1rbtSRqKxTvirZDDOct1k',
                'timestamp': 2085848896000,
                'nonce': 'd73b41172d6deca2285e8e58533db082',
                'signature': (
                    'f47526dec80c4773815fb1121058c2e3bcc531d1224b683e8babf76e52b0ba9c'
                ),
            },
            'id': 'auth',
        }
        assert msg == expected

    async def dummy_generator():
        yield

    ws = MagicMock()
    ws._response.url.host = 'ws.lightstream.bitflyer.com'
    ws._response._session.__dict__['_apis'] = {
        'bitflyer': (
            'Pcm1rbtSRqKxTvirZDDOct1k',
            b'AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4',
        ),
    }
    ws.send_json.side_effect = dummy_send
    # ws.__aiter__.side_effect = dummy_generator
    # TODO: Test __aiter__ code, Currently MagicMock does not have __aiter__
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        with pytest.raises(TypeError):
            await pybotters.ws.Auth.bitflyer(ws)
    elif sys.version_info.major == 3 and sys.version_info.minor > 7:
        await pybotters.ws.Auth.bitflyer(ws)
    else:
        raise RuntimeError(f'Unsupported Python version: {sys.version}')


@pytest.mark.asyncio
async def test_liquid_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)

    async def dummy_send(msg):
        expected = {
            'event': 'quoine:auth_request',
            'data': {
                'path': '/realtime',
                'headers': {
                    'X-Quoine-Auth': (
                        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL3JlYWx0aW1lI'
                        'iwibm9uY2UiOiIyMDg1ODQ4ODk2MDAwIiwidG9rZW5faWQiOiI1RGp6Z21RWFJ'
                        'rc1FOREJRNUcxck5JdjcifQ.9BS3xGAJW_Ggr_0LzfH1TNf8LjFeXl95yGvn9A'
                        '7sKm4'
                    )
                },
            },
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = 'tap.liquid.com'
    ws._response._session.__dict__['_apis'] = {
        'liquid': (
            '5DjzgmQXRksQNDBQ5G1rNIv7',
            b'WXlZDDzyjWtz1bd7MsGoXPMEohkdUuB95HHgBbKwKBaCyDrp',
        ),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.liquid(ws)


@pytest.mark.asyncio
async def test_ftx_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)

    async def dummy_send(msg):
        expected = {
            'op': 'login',
            'args': {
                'key': 'J6vXtiZunV4lsRWoLHNYNiCa',
                'sign': (
                    'b810f0085a627ea8cad1b2923d63ee05916166a464ab4f89e366abfc7f76a8ac'
                ),
                'time': 2085848896000,
            },
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = 'ftx.com'
    ws._response._session.__dict__['_apis'] = {
        'ftx': (
            'J6vXtiZunV4lsRWoLHNYNiCa',
            b'8ORbaZIrTNcV6Lw48x12RrEzuT0YqbCiluml7LITzG2ud2Nf',
        ),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.ftx(ws)


@pytest.mark.asyncio
async def test_phemex_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)

    async def dummy_send(msg):
        expected = {
            'method': 'user.auth',
            'params': [
                'API',
                '9kYxQXZ6PrR8h17lsVdDcpnJ',
                '196f317edfa0662ec3d388099683b40a25607919ca3546b131108b9ee5cbed4a',
                2085848956,
            ],
            'id': 123,
        }
        assert msg == expected

    async def dummy_generator():
        yield

    ws = MagicMock()
    ws._response.url.host = 'phemex.com'
    ws._response._session.__dict__['_apis'] = {
        'phemex': (
            '9kYxQXZ6PrR8h17lsVdDcpnJ',
            b'ZBAUiPBTQOjYgTihYnZMw2HFkTooufRnNY5iuahBPMspRYQJ',
        ),
    }
    ws.send_json.side_effect = dummy_send
    # ws.__aiter__.side_effect = dummy_generator
    # TODO: Test __aiter__ code, Currently MagicMock does not have __aiter__
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        with pytest.raises(TypeError):
            await pybotters.ws.Auth.phemex(ws)
    elif sys.version_info.major == 3 and sys.version_info.minor > 7:
        await pybotters.ws.Auth.phemex(ws)
    else:
        raise RuntimeError(f'Unsupported Python version: {sys.version}')


@pytest.mark.asyncio
async def test_okx_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)

    async def dummy_send(msg):
        expected = {
            'op': 'login',
            'args': [
                {
                    'apiKey': 'gYmX9fr0kqqxptUlDKESxetg',
                    'passphrase': 'MyPassphrase123',
                    'timestamp': '2085848896',
                    'sign': '6QVd7Mgd70We2/oDJr0+KnqxXZ+Gf1zIIl3qJk/Pqx8=',
                }
            ],
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = 'ws.okx.com'
    ws._response._session.__dict__['_apis'] = {
        'okx': (
            'gYmX9fr0kqqxptUlDKESxetg',
            b'YUJHBdFNrbz7atmV3f261ZhdRffTo4S9KZKC7C7qdqcHbRR4',
            'MyPassphrase123',
        ),
    }
    ws.send_json.side_effect = dummy_send
    # TODO: Test __aiter__ code, Currently MagicMock does not have __aiter__
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        with pytest.raises(TypeError):
            await pybotters.ws.Auth.okx(ws)
    elif sys.version_info.major == 3 and sys.version_info.minor > 7:
        await pybotters.ws.Auth.okx(ws)
    else:
        raise RuntimeError(f'Unsupported Python version: {sys.version}')


@pytest.mark.asyncio
async def test_bitget_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)

    async def dummy_send(msg):
        expected = {
            'op': 'login',
            'args': [
                {
                    'apiKey': 'jbcfbye8AJzXxXwMKluXM12t',
                    'passphrase': 'MyPassphrase123',
                    'timestamp': '2085848896',
                    'sign': 'QAyHX41dxONjr5Wx/SVfHGxEo5Q+NECtOh22tZ7ledA=',
                }
            ],
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = 'ws.okx.com'
    ws._response._session.__dict__['_apis'] = {
        'okx': (
            'jbcfbye8AJzXxXwMKluXM12t',
            b'mVd40qhnarPtxk3aqg0FCyY1qlTgBOKOXEcmMYfkerGUKmvr',
            'MyPassphrase123',
        ),
    }
    ws.send_json.side_effect = dummy_send
    # TODO: Test __aiter__ code, Currently MagicMock does not have __aiter__
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        with pytest.raises(TypeError):
            await pybotters.ws.Auth.okx(ws)
    elif sys.version_info.major == 3 and sys.version_info.minor > 7:
        await pybotters.ws.Auth.okx(ws)
    else:
        raise RuntimeError(f'Unsupported Python version: {sys.version}')


def test_websocketrunner(mocker: pytest_mock.MockerFixture):
    create_task = mocker.patch('asyncio.create_task')
    ret_run_forever = mocker.Mock()
    run_forever = mocker.patch.object(
        pybotters.ws.WebSocketRunner, '_run_forever', ret_run_forever
    )
    session = mocker.Mock()
    send_str = mocker.Mock()
    send_bytes = mocker.Mock()
    send_json = mocker.Mock()
    hdlr_str = mocker.Mock()
    hdlr_bytes = mocker.Mock()
    hdlr_json = mocker.Mock()
    ws = pybotters.ws.WebSocketRunner(
        'wss://example.com',
        session,
        send_str=send_str,
        send_bytes=send_bytes,
        send_json=send_json,
        hdlr_str=hdlr_str,
        hdlr_bytes=hdlr_bytes,
        hdlr_json=hdlr_json,
    )
    assert isinstance(ws, pybotters.ws.WebSocketRunner)
    assert run_forever.called
    assert run_forever.call_args == [
        ('wss://example.com', session),
        {
            'send_str': send_str,
            'send_bytes': send_bytes,
            'send_json': send_json,
            'hdlr_str': hdlr_str,
            'hdlr_bytes': hdlr_bytes,
            'hdlr_json': hdlr_json,
            'auth': pybotters.auth.Auth,
        },
    ]
    assert create_task.called
    assert create_task.call_args == [(ret_run_forever.return_value,)]
