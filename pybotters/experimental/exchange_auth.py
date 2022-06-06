import asyncio
import base64
import datetime
import secrets
from typing import Any, Dict, TYPE_CHECKING

import aiohttp
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST
from aiohttp.typedefs import JSONEncoder
from multidict import MultiDict
from yarl import URL

from .helpers import BaseAuth

if TYPE_CHECKING:
    from .client_reqrep import ClientRequest
    from .client_ws import ClientWebSocketResponse


class BybitAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        timestamp = self.get_milliseconds()
        auth_params = {
            "api_key": self.key,
            "timestamp": timestamp,
        }
        if url.query:
            query = MultiDict(url.query)
            query.update(auth_params)
            query_string = self.urlencode(sorted(query.items()), quote=False)
            sign = self.sha256_hexdigest(query_string.encode())
            query.update({"sign": sign})
            request.url = url.with_query(query)
        if data:
            data.update(auth_params)
            query_string = self.urlencode(sorted(data.items()), quote=False)
            sign = self.sha256_hexdigest(query_string.encode())
            data.update({"sign": sign})
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        expires = str(self.get_milliseconds(1.0))
        msg = f"{request.method}/realtime{expires}".encode()
        signature = self.sha256_hexdigest(msg)

        await ws.send_json({"op": "auth", "args": [self.key, expires, signature]})

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data='{"op":"ping"}',
            heartbeat=30.0,
        )


class BinanceAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        query = MultiDict(url.query)
        if data:
            query.update(data)
            request.data = None

        timestamp = str(self.get_milliseconds())
        query.update({"timestamp": timestamp})
        if url.name != "batchOrders":
            query_string = self.urlencode(query, doseq=True, safe="@")
        else:
            query_string = self.urlencode(query, safe="@")
            query_string = query_string.replace("%27", "%22")
        signature = self.sha256_hexdigest(query_string.encode())

        query.update({"signature": signature})
        if url.name != "batchOrders":
            query_string = self.urlencode(query, doseq=True, safe="@")
        else:
            query_string = self.urlencode(query, safe="@")
            query_string = query_string.replace("%27", "%22")
        request.url = URL.build(
            scheme=url.scheme,
            host=url.raw_host,
            port=url.port,
            path=url.raw_path,
            query_string=query_string,
            encoded=True,
        )

        headers.update({"X-MBX-APIKEY": self.key})

    @staticmethod
    async def wsratelimit(ws: "ClientWebSocketResponse") -> None:
        session = ws._response._session

        async with session.get("https://api.binance.com/api/v3/time"):
            pass

        await asyncio.sleep(0.25)  # limit of 5 incoming messages per second


class bitFlyerAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            if method in (METH_POST):
                value += request.data._value

        timestamp = str(self.get_milliseconds())
        msg = f"{timestamp}{method}{url.raw_path_qs}".encode() + value
        sign = self.sha256_hexdigest(msg)

        headers.update(
            {
                "ACCESS-KEY": self.key,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-SIGN": sign,
            }
        )

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        timestamp = self.get_milliseconds()
        nonce = secrets.token_hex(16)
        signature = self.sha256_hexdigest(f"{timestamp}{nonce}".encode())

        ws._acquire_lock()
        await ws.send_json(
            {
                "method": "auth",
                "params": {
                    "api_key": self.key,
                    "timestamp": timestamp,
                    "nonce": nonce,
                    "signature": signature,
                },
                "id": 120,
            }
        )
        async with ws._lock:
            while ws._queue is not None:
                msg: aiohttp.WSMessage = await ws._queue.get()
                data: Dict[str, Any] = msg.json()
                if data.get("id") == 120:
                    ws._release_lock()


class GMOCoinAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        if not self.ishandshake(headers):
            value = b""
            if data:
                request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
                if method == METH_POST:
                    value += request.data._value

            timestamp = str(self.get_milliseconds())
            path = "/" + "/".join(url.parts[2:])
            msg = f"{timestamp}{method}{path}".encode() + value
            sign = self.sha256_hexdigest(msg)

            headers.update(
                {"API-KEY": self.key, "API-TIMESTAMP": timestamp, "API-SIGN": sign}
            )

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        if not ws._response.url.path.startswith("/ws/private"):
            return

        session = ws._response._session
        while True:
            await asyncio.sleep(1800.0)

            if session.closed:
                break

            async with session.put(
                "https://api.coin.z.com/private/v1/ws-auth",
                data={"token": ws._response.url.name},
                auth=self,
            ) as resp:
                data = await resp.json()

            if data["status"] != 0:
                break

    @staticmethod
    async def wsratelimit(ws: "ClientWebSocketResponse") -> None:
        session = ws._response._session

        async with session.get("https://api.coin.z.com/public/v1/status"):
            pass

        await asyncio.sleep(1.0)


class LiquidAuth(BaseAuth):
    def _jwt(self, path: str, json_serialize: JSONEncoder) -> str:
        json_header = json_serialize(
            {"typ": "JWT", "alg": "HS256"},
        ).encode()
        json_payload = json_serialize(
            {
                "path": path,
                "nonce": str(self.get_milliseconds()),
                "token_id": self.key,
            },
        ).encode()
        segments = [
            base64.urlsafe_b64encode(json_header).replace(b"=", b""),
            base64.urlsafe_b64encode(json_payload).replace(b"=", b""),
        ]
        signing_input = b".".join(segments)
        signature = self.sha256_digest(signing_input)
        segments.append(base64.urlsafe_b64encode(signature).replace(b"=", b""))
        return b".".join(segments).decode()

    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)

        jwt = self._jwt(url.raw_path_qs, request.json_serialize)

        headers.update({"X-Quoine-API-Version": "2", "X-Quoine-Auth": jwt})

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        jwt = self._jwt("/realtime", request.json_serialize)

        await ws.send_json(
            {
                "event": "quoine:auth_request",
                "data": {
                    "path": "/realtime",
                    "headers": {"X-Quoine-Auth": jwt},
                },
            },
        )

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data='{"event":"pusher:ping","data":{}}',
            heartbeat=60.0,
        )


class bitbankAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            value += request.data._value

        nonce = str(self.get_milliseconds())
        msg = nonce.encode()
        if method == METH_GET:
            msg += url.raw_path_qs.encode()
        elif method == METH_POST:
            msg += value
        signature = self.sha256_hexdigest(msg)

        headers.update(
            {
                "ACCESS-KEY": self.key,
                "ACCESS-NONCE": nonce,
                "ACCESS-SIGNATURE": signature,
            }
        )

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data="2",
            heartbeat=15.0,
        )


class FTXAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        if not self.ishandshake(headers):
            value = b""
            if data:
                request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
                value += request.data._value

            ts = str(self.get_milliseconds())
            path = URL.build(path=url.path, query_string=url.raw_query_string).path_qs
            msg = f"{ts}{method}{path}".encode() + value
            sign = self.sha256_hexdigest(msg)

            headers.update({"FTX-KEY": self.key, "FTX-SIGN": sign, "FTX-TS": ts})

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        ts = self.get_milliseconds()
        sign = self.sha256_hexdigest(f"{ts}websocket_login".encode())
        data = {
            "op": "login",
            "args": {"key": self.key, "sign": sign, "time": ts},
        }

        if "FTX-SUBACCOUNT" in request.headers:
            subaccount = request.headers["FTX-SUBACCOUNT"]
            data["args"]["subaccount"] = subaccount

        await ws.send_json(data)

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data='{"op":"ping"}',
            heartbeat=15.0,
        )


class BitMEXAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            value += request.data._value

        expires = str(self.get_milliseconds(5.0))
        msg = f"{method}{url.raw_path_qs}{expires}".encode() + value
        signature = self.sha256_hexdigest(msg)

        headers.update(
            {"api-expires": expires, "api-key": self.key, "api-signature": signature}
        )


class PhemexAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            if method == METH_POST:
                value += request.data._value

        expiry = str(self.get_seconds(60.0))
        msg = f"{url.raw_path}{url.query_string}{expiry}".encode() + value
        signature = self.sha256_hexdigest(msg)

        headers.update(
            {
                "x-phemex-access-token": self.key,
                "x-phemex-request-expiry": expiry,
                "x-phemex-request-signature": signature,
            }
        )

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        expiry = self.get_seconds(2 * 60)
        signature = self.sha256_hexdigest(f"{self.key}{expiry}".encode())

        ws._acquire_lock()
        await ws.send_json(
            {
                "method": "user.auth",
                "params": ["API", self.key, signature, expiry],
                "id": 1234,
            }
        )
        async with ws._lock:
            while ws._queue is not None:
                msg: aiohttp.WSMessage = await ws._queue.get()
                data: Dict[str, Any] = msg.json()
                if data.get("id") == 1234:
                    ws._release_lock()

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data='{"method":"server.ping","params":[],"id":123}',
            heartbeat=10.0,
        )


class CoincheckAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            value += request.data._value

        nonce = str(self.get_milliseconds())
        msg = f"{nonce}{url}".encode() + value
        signature = self.sha256_hexdigest(msg)

        headers.update(
            {
                "ACCESS-KEY": self.key,
                "ACCESS-NONCE": nonce,
                "ACCESS-SIGNATURE": signature,
            }
        )


class OKXAuth(BaseAuth):
    @staticmethod
    def isdemo(request: "ClientRequest"):
        return request.headers.get("x-simulated-trading") == "1"

    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            value += request.data._value

        timestamp = f'{datetime.datetime.utcnow().isoformat(timespec="milliseconds")}Z'
        msg = f"{timestamp}{method}{url.raw_path_qs}".encode() + value
        sign = base64.b64encode(self.sha256_digest(msg)).decode()

        headers.update(
            {
                "OK-ACCESS-KEY": self.key,
                "OK-ACCESS-SIGN": sign,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase,
            }
        )

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        timestamp = self.get_seconds()
        msg = f"{timestamp}GET/users/self/verify".encode()
        sign = base64.b64encode(self.sha256_digest(msg)).decode()

        ws._acquire_lock()
        await ws.send_json(
            {
                "op": "login",
                "args": [
                    {
                        "apiKey": self.key,
                        "passphrase": self.passphrase,
                        "timestamp": timestamp,
                        "sign": sign,
                    }
                ],
            }
        )
        async with ws._lock:
            while ws._queue is not None:
                msg: aiohttp.WSMessage = await ws._queue.get()
                data: Dict[str, Any] = msg.json()
                if data.get("event") in ("login", "error"):
                    ws._release_lock()

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data="ping",
            heartbeat=15.0,
        )


class BitgetAuth(BaseAuth):
    def sign(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        value = b""
        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)
            value += request.data._value

        timestamp = str(self.get_milliseconds())
        msg = f"{timestamp}{method}{url.raw_path_qs}".encode() + value
        sign = base64.b64encode(self.sha256_digest(msg)).decode()

        headers.update(
            {
                "ACCESS-KEY": self.key,
                "ACCESS-SIGN": sign,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": self.passphrase,
            }
        )

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        timestamp = self.get_seconds()
        msg = f"{timestamp}GET/user/verify".encode()
        sign = base64.b64encode(self.sha256_digest(msg)).decode()

        await ws.send_json(
            {
                "op": "login",
                "args": [
                    {
                        "api_key": self.key,
                        "passphrase": self.passphrase,
                        "timestamp": timestamp,
                        "sign": sign,
                    }
                ],
            }
        )

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data="ping",
            heartbeat=25.0,
        )


class MEXCAuth(BaseAuth):
    def _sign_v2(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        if data:
            request.data = self.to_jsonpayload(data, dumps=request.json_serialize)

        query_string = ""
        value = b""
        if method in (METH_GET, METH_DELETE):
            query_string += url.raw_query_string
        elif method in (METH_POST):
            if data:
                value += request.data._value

        timestamp = str(self.get_milliseconds())
        msg = f"{self.key}{timestamp}{query_string}".encode() + value
        signature = self.sha256_hexdigest(msg)

        headers.update(
            {
                "ApiKey": self.key,
                "Request-Time": timestamp,
                "Signature": signature,
            }
        )

    def _sign_v3(self, request: "ClientRequest") -> None:
        method = request.method
        url = request.url
        data: Dict[str, Any] = request.data
        headers = request.headers

        query = MultiDict(url.query)
        if data:
            query.update(data)
            request.data = None

        timestamp = str(self.get_milliseconds())
        query.update({"timestamp": timestamp})
        query_string = self.urlencode(query, doseq=True, safe="@")
        signature = self.sha256_hexdigest(query_string.encode())

        query.update({"signature": signature})
        query_string = self.urlencode(query, doseq=True, safe="@")
        request.url = URL.build(
            scheme=url.scheme,
            host=url.raw_host,
            port=url.port,
            path=url.raw_path,
            query_string=query_string,
            encoded=True,
        )

        headers.update({"X-MEXC-APIKEY": self.key})

    def sign(self, request: "ClientRequest") -> None:
        if request.url.host in ("www.mexc.com", "contract.mexc.com"):
            self._sign_v2(request)
        elif request.url.host in ("api.mexc.com"):
            self._sign_v3(request)

    async def wssign(self, ws: "ClientWebSocketResponse") -> None:
        request = ws._response.request_info

        timestamp = self.get_milliseconds()
        sign = self.sha256_hexdigest(f"{self.key}{timestamp}".encode())

        await ws.send_json(
            {
                "method": "login",
                "param": {
                    "apiKey": self.key,
                    "reqTime": timestamp,
                    "signature": sign,
                },
            }
        )

    @classmethod
    async def wsping(cls, ws: "ClientWebSocketResponse") -> None:
        await cls._wsping(
            coro=ws.send_str,
            data='{"method":"ping"}',
            heartbeat=10.0,
        )
