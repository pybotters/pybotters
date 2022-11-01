from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Callable

import aiohttp
from aiohttp.formdata import FormData
from aiohttp.hdrs import METH_DELETE, METH_GET
from aiohttp.payload import JsonPayload
from multidict import CIMultiDict, MultiDict
from yarl import URL


class Auth:
    @staticmethod
    def bybit(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        if url.scheme == "https":
            expires = str(int((time.time() - 5.0) * 1000))
            recv_window = (
                "recv_window" if not url.path.startswith("/spot") else "recvWindow"
            )
            auth_params = {"api_key": key, "timestamp": expires, recv_window: 10000}
            if method in (METH_GET, METH_DELETE):
                query = MultiDict(url.query)
                query.extend(auth_params)
                query_string = "&".join(f"{k}={v}" for k, v in sorted(query.items()))
                sign = hmac.new(
                    secret, query_string.encode(), hashlib.sha256
                ).hexdigest()
                query.extend({"sign": sign})
                url = url.with_query(query)
                args = (method, url)
            else:
                data.update(auth_params)
                body = FormData(sorted(data.items()))()
                sign = hmac.new(secret, body._value, hashlib.sha256).hexdigest()
                body._value += f"&sign={sign}".encode()
                body._size = len(body._value)
                kwargs.update({"data": body})
        elif url.scheme == "wss":
            query = MultiDict(url.query)
            expires = str(int((time.time() + 5.0) * 1000))
            path = f"{method}/realtime{expires}"
            signature = hmac.new(secret, path.encode(), hashlib.sha256).hexdigest()
            query.extend({"api_key": key, "expires": expires, "signature": signature})
            url = url.with_query(query)
            args = (method, url)

        return args

    @staticmethod
    def binance(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        expires = str(int(time.time() * 1000))
        if method == METH_GET:
            if url.scheme == "https":
                query = MultiDict(url.query)
                query.extend({"timestamp": expires})
                query_string = "&".join(f"{k}={v}" for k, v in query.items())
                signature = hmac.new(
                    secret, query_string.encode(), hashlib.sha256
                ).hexdigest()
                query.extend({"signature": signature})
                url = url.with_query(query)
                args = (
                    method,
                    url,
                )
        else:
            data.update({"timestamp": expires})
            # patch (issue #190, #192)
            if url.path != "/api/v3/userDataStream":
                body = FormData(data)()
            else:
                body = FormData()()
            signature = hmac.new(secret, body._value, hashlib.sha256).hexdigest()
            # patch (issue #190, #192)
            if url.path != "/api/v3/userDataStream":
                body._value += f"&signature={signature}".encode()
            body._size = len(body._value)
            kwargs.update({"data": body})
        headers.update({"X-MBX-APIKEY": key})

        return args

    @staticmethod
    def bitflyer(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = url.raw_path_qs
        body = JsonPayload(data) if data else FormData(data)()
        timestamp = str(int(time.time() * 1000))
        text = f"{timestamp}{method}{path}".encode() + body._value
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {"ACCESS-KEY": key, "ACCESS-TIMESTAMP": timestamp, "ACCESS-SIGN": signature}
        )

        return args

    @staticmethod
    def gmocoin(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = "/" + "/".join(url.parts[2:])
        body = JsonPayload(data) if data else FormData(data)()
        timestamp = str(int(time.time() * 1000))
        # PUT and DELETE requests do not require payload inclusion
        if method == "POST":
            text = f"{timestamp}{method}{path}".encode() + body._value
        else:
            text = f"{timestamp}{method}{path}".encode()
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {"API-KEY": key, "API-TIMESTAMP": timestamp, "API-SIGN": signature}
        )

        return args

    @staticmethod
    def liquid(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        json_payload = json.dumps(
            {
                "path": url.raw_path_qs,
                "nonce": str(int(time.time() * 1000)),
                "token_id": key,
            },
            separators=(",", ":"),
        ).encode()
        json_header = json.dumps(
            {"typ": "JWT", "alg": "HS256"},
            separators=(",", ":"),
        ).encode()
        segments = [
            base64.urlsafe_b64encode(json_header).replace(b"=", b""),
            base64.urlsafe_b64encode(json_payload).replace(b"=", b""),
        ]
        signing_input = b".".join(segments)
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        segments.append(base64.urlsafe_b64encode(signature).replace(b"=", b""))
        encoded_string = b".".join(segments).decode()
        body = JsonPayload(data) if data else FormData(data)()
        kwargs.update({"data": body})
        headers.update({"X-Quoine-API-Version": "2", "X-Quoine-Auth": encoded_string})

        return args

    @staticmethod
    def bitbank(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = url.raw_path_qs
        body = JsonPayload(data) if data else FormData(data)()
        nonce = str(int(time.time() * 1000))
        if method == METH_GET:
            text = f"{nonce}{path}".encode()
        else:
            text = nonce.encode() + body._value
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {"ACCESS-KEY": key, "ACCESS-NONCE": nonce, "ACCESS-SIGNATURE": signature}
        )

        return args

    @staticmethod
    def ftx(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = url.raw_path_qs
        body = JsonPayload(data) if data else FormData(data)()
        ts = str(int(time.time() * 1000))
        text = f"{ts}{method}{path}".encode() + body._value
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update({"FTX-KEY": key, "FTX-SIGN": signature, "FTX-TS": ts})

        return args

    @staticmethod
    def bitmex(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = url.raw_path_qs if url.scheme == "https" else "/realtime"
        body = FormData(data)()
        expires = str(int((time.time() + 5.0) * 1000))
        message = f"{method}{path}{expires}".encode() + body._value
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {"api-expires": expires, "api-key": key, "api-signature": signature}
        )

        return args

    @staticmethod
    def phemex(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        path = url.raw_path
        query = url.query_string
        body = JsonPayload(data) if data else FormData(data)()
        expiry = str(int((time.time() + 60.0)))
        formula = f"{path}{query}{expiry}".encode() + body._value
        signature = hmac.new(secret, formula, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {
                "x-phemex-access-token": key,
                "x-phemex-request-expiry": expiry,
                "x-phemex-request-signature": signature,
            }
        )

        return args

    @staticmethod
    def coincheck(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        nonce = str(int(time.time() * 1000))
        body = FormData(data)()
        message = f"{nonce}{url}".encode() + body._value
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {"ACCESS-KEY": key, "ACCESS-NONCE": nonce, "ACCESS-SIGNATURE": signature}
        )

        return args

    @staticmethod
    def okx(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        api_name = NameSelector.okx(headers)
        key: str = session.__dict__["_apis"][api_name][0]
        secret: bytes = session.__dict__["_apis"][api_name][1]
        passphrase: str = session.__dict__["_apis"][api_name][2]

        timestamp = f'{datetime.datetime.utcnow().isoformat(timespec="milliseconds")}Z'
        body = JsonPayload(data) if data else FormData(data)()
        text = f"{timestamp}{method}{url.raw_path_qs}".encode() + body._value
        sign = base64.b64encode(
            hmac.new(secret, text, hashlib.sha256).digest()
        ).decode()
        kwargs.update({"data": body})
        headers.update(
            {
                "OK-ACCESS-KEY": key,
                "OK-ACCESS-SIGN": sign,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": passphrase,
                "Content-Type": "application/json",
            }
        )

        return args

    @staticmethod
    def bitget(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]
        passphase: str = session.__dict__["_apis"][Hosts.items[url.host].name][2]

        path = url.raw_path_qs
        body = JsonPayload(data) if data else FormData(data)()
        timestamp = str(int(time.time() * 1000))
        msg = f"{timestamp}{method}{path}".encode() + body._value
        sign = base64.b64encode(
            hmac.new(secret, msg, digestmod=hashlib.sha256).digest()
        ).decode()
        kwargs.update({"data": body})
        headers.update(
            {
                "Content-Type": "application/json",
                "ACCESS-KEY": key,
                "ACCESS-SIGN": sign,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": passphase,
            }
        )

        return args

    @staticmethod
    def mexc_v2(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        timestamp = str(int(time.time() * 1000))
        if method in (METH_GET, METH_DELETE) and url.scheme == "https":
            query = URL.build(query=sorted(url.query.items()))
            parameter = query.raw_query_string.encode()
        else:
            body = JsonPayload(data) if data else FormData(data)()
            parameter = body._value
            kwargs.update({"data": body})
        signature = hmac.new(
            secret, f"{key}{timestamp}".encode() + parameter, hashlib.sha256
        ).hexdigest()
        headers.update(
            {
                "ApiKey": key,
                "Request-Time": timestamp,
                "Signature": signature,
                "Content-Type": "application/json",
            }
        )

        return args

    @staticmethod
    def mexc_v3(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        timestamp = str(int(time.time() * 1000))
        query = MultiDict(url.query)
        body = FormData(data)()

        if query:
            query.extend({"timestamp": timestamp})
            url = url.with_query(query)
            query = MultiDict(url.query)
        else:
            body._value += f"&timestamp={timestamp}".encode()

        query_string = url.raw_query_string.encode()
        signature = hmac.new(
            secret, query_string + body._value, hashlib.sha256
        ).hexdigest()

        if query:
            query.extend({"signature": signature})
        else:
            body._value += f"&signature={signature}".encode()
            body._size += len(body._value)

        url = url.with_query(query)
        args = (method, url)
        kwargs.update({"data": body._value})
        headers.update({"X-MEXC-APIKEY": key, "Content-Type": "application/json"})

        return args

    @staticmethod
    def kucoin(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]
        passphrase: str = session.__dict__["_apis"][Hosts.items[url.host].name][2]

        now = int(time.time() * 1000)
        if method == "GET":
            str_to_sign = str(now) + method + url.path_qs
        else:
            body = JsonPayload(data) if data else FormData(data)()
            headers["Content-Type"] = "application/json"
            kwargs.update({"data": body._value})
            str_to_sign = str(now) + method + url.path + body._value.decode()

        signature = base64.b64encode(
            hmac.new(secret, str_to_sign.encode("utf-8"), hashlib.sha256).digest()
        ).decode()
        passphrase = base64.b64encode(
            hmac.new(secret, passphrase.encode("utf-8"), hashlib.sha256).digest()
        ).decode()
        headers.update(
            {
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": str(now),
                "KC-API-KEY": key,
                "KC-API-PASSPHRASE": passphrase,
                "KC-API-KEY-VERSION": "2",
            }
        )
        return args


@dataclass
class Item:
    name: str | Callable[[CIMultiDict], str]
    func: Any


class NameSelector:
    @staticmethod
    def okx(headers: CIMultiDict) -> str:
        if "x-simulated-trading" in headers:
            if headers["x-simulated-trading"] == "1":
                return "okx_demo"
        return "okx"


class Hosts:
    items = {
        "api.bybit.com": Item("bybit", Auth.bybit),
        "api.bytick.com": Item("bybit", Auth.bybit),
        "stream.bybit.com": Item("bybit", Auth.bybit),
        "stream.bytick.com": Item("bybit", Auth.bybit),
        "api-testnet.bybit.com": Item("bybit_testnet", Auth.bybit),
        "stream-testnet.bybit.com": Item("bybit_testnet", Auth.bybit),
        "api.binance.com": Item("binance", Auth.binance),
        "api1.binance.com": Item("binance", Auth.binance),
        "api2.binance.com": Item("binance", Auth.binance),
        "api3.binance.com": Item("binance", Auth.binance),
        "stream.binance.com": Item("binance", Auth.binance),
        "fapi.binance.com": Item("binance", Auth.binance),
        "fstream.binance.com": Item("binance", Auth.binance),
        "fstream-auth.binance.com": Item("binance", Auth.binance),
        "dapi.binance.com": Item("binance", Auth.binance),
        "dstream.binance.com": Item("binance", Auth.binance),
        "vapi.binance.com": Item("binance", Auth.binance),
        "vstream.binance.com": Item("binance", Auth.binance),
        "testnet.binancefuture.com": Item("binance_testnet", Auth.binance),
        "stream.binancefuture.com": Item("binance_testnet", Auth.binance),
        "dstream.binancefuture.com": Item("binance_testnet", Auth.binance),
        "testnet.binanceops.com": Item("binance_testnet", Auth.binance),
        "testnetws.binanceops.com": Item("binance_testnet", Auth.binance),
        "api.bitflyer.com": Item("bitflyer", Auth.bitflyer),
        "api.coin.z.com": Item("gmocoin", Auth.gmocoin),
        "api.liquid.com": Item("liquid", Auth.liquid),
        "api.bitbank.cc": Item("bitbank", Auth.bitbank),
        "ftx.com": Item("ftx", Auth.ftx),
        "www.bitmex.com": Item("bitmex", Auth.bitmex),
        "testnet.bitmex.com": Item("bitmex_testnet", Auth.bitmex),
        "api.phemex.com": Item("phemex", Auth.phemex),
        "testnet-api.phemex.com": Item("phemex_testnet", Auth.phemex),
        "coincheck.com": Item("coincheck", Auth.coincheck),
        "www.okx.com": Item(NameSelector.okx, Auth.okx),
        "aws.okx.com": Item(NameSelector.okx, Auth.okx),
        "api.bitget.com": Item("bitget", Auth.bitget),
        "www.mexc.com": Item("mexc", Auth.mexc_v2),
        "contract.mexc.com": Item("mexc", Auth.mexc_v2),
        "api.mexc.com": Item("mexc", Auth.mexc_v3),
        "api.kucoin.com": Item("kucoinspot", Auth.kucoin),
        "api-futures.kucoin.com": Item("kucoinfuture", Auth.kucoin),
    }
