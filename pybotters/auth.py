from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from aiohttp.formdata import FormData
from aiohttp.hdrs import METH_DELETE, METH_GET
from aiohttp.payload import JsonPayload
from multidict import CIMultiDict, MultiDict
from yarl import URL

from pybotters.helpers import hyperliquid

if TYPE_CHECKING:
    from collections.abc import Callable

    import aiohttp


class Auth:
    @staticmethod
    def bybit(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        timestamp = str(int(time.time() * 1000))
        query_string = url.raw_query_string
        body = JsonPayload(data) if data else FormData(data)()
        text = f"{timestamp}{key}{query_string}".encode() + body._value
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {
                "X-BAPI-API-KEY": key,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
            }
        )

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

        # Do not sign WebSocket upgrade requests
        if headers.get("Upgrade") == "websocket":
            args = (method, url)
            return args

        headers.update({"X-MBX-APIKEY": key})

        # NOTE: Security Type `USER_STREAM` patch (Issue #192), Only edit header
        if url.name in {"userDataStream", "listen-key", "listenKey"}:
            args = (method, url)
            return args

        expires = str(int(time.time() * 1000))
        query = MultiDict(url.query)
        body = FormData(data)()

        query.extend({"timestamp": expires})
        url = url.with_query(query)
        query = MultiDict(url.query)

        query_string = url.raw_query_string.encode()
        signature = hmac.new(
            secret, query_string + body._value, hashlib.sha256
        ).hexdigest()

        query.extend({"signature": signature})
        url = url.with_query(query)
        args = (method, url)
        kwargs.update({"data": body})

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
        window = headers.get("ACCESS-TIME-WINDOW", "")
        if method == METH_GET:
            text = f"{nonce}{window}{path}".encode()
        else:
            text = f"{nonce}{window}".encode() + body._value
        signature = hmac.new(secret, text, hashlib.sha256).hexdigest()
        kwargs.update({"data": body})
        headers.update(
            {
                "ACCESS-KEY": key,
                "ACCESS-REQUEST-TIME": nonce,
                "ACCESS-SIGNATURE": signature,
            }
        )

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
        api_name = DynamicNameSelector.okx(args, kwargs)
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

        query.extend({"timestamp": timestamp})
        url = url.with_query(query)
        query = MultiDict(url.query)

        query_string = url.raw_query_string.encode()
        signature = hmac.new(
            secret, query_string + body._value, hashlib.sha256
        ).hexdigest()

        query.extend({"signature": signature})

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
        body = JsonPayload(data) if data else FormData(data)()
        if body._value:
            kwargs.update({"data": body})

        str_to_sign = f"{now}{method}{url.path_qs}".encode() + body._value

        signature = base64.b64encode(
            hmac.new(secret, str_to_sign, hashlib.sha256).digest()
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

    @staticmethod
    def okj(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}
        headers: CIMultiDict = kwargs["headers"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]
        passphrase: str = session.__dict__["_apis"][Hosts.items[url.host].name][2]

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
    def bittrade(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method, url = args
        data = kwargs["data"]

        session: aiohttp.ClientSession = kwargs["session"]
        key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]
        secret: bytes = session.__dict__["_apis"][Hosts.items[url.host].name][1]

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        query = MultiDict(url.query)
        query.extend(
            {
                "AccessKeyId": key,
                "SignatureMethod": "HmacSHA256",
                "SignatureVersion": "2",
                "Timestamp": timestamp,
            }
        )
        sorted_query = MultiDict(sorted(query.items()))
        # NOTE: yarl.URL.raw_query_string does not encode colons(:), so use urllib.parse.urlencode instead
        sorted_raw_query_string = urlencode(sorted_query)
        sign_str = (
            f"{method}\n{url.host}\n{url.raw_path}\n{sorted_raw_query_string}".encode()
        )
        signature = base64.b64encode(
            hmac.new(secret, sign_str, hashlib.sha256).digest()
        ).decode()
        query.extend({"Signature": signature})

        url = url.with_query(query)

        if data:
            kwargs.update({"data": JsonPayload(data)})

        return (method, url)

    @staticmethod
    def hyperliquid(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        url: URL = args[1]
        data: dict[str, Any] = kwargs["data"] or {}

        session: aiohttp.ClientSession = kwargs["session"]
        secret_key: str = session.__dict__["_apis"][Hosts.items[url.host].name][0]

        if url.path.startswith("/info"):
            return args

        action: dict[str, Any] = data.get("action", {})
        nonce: int = data.setdefault("nonce", hyperliquid.get_timestamp_ms())
        vault_address: str | None = data.get("vaultAddress")

        if "signature" not in data:
            eip712_typed_data: tuple[
                hyperliquid.EIP712Domain,
                hyperliquid.MessageTypes,
                hyperliquid.MessageData,
            ]
            # sign_l1_action
            if "hyperliquidChain" not in action:
                is_mainnet = isinstance(url.host, str) and "testnet" not in url.host
                eip712_typed_data = hyperliquid.construct_l1_action(
                    action, nonce, is_mainnet, vault_address
                )
            # sign_user_signed_action
            else:
                eip712_typed_data = hyperliquid.construct_user_signed_action(action)
                data["action"] = eip712_typed_data[2]  # MessageData

            signature = hyperliquid.sign_typed_data(secret_key, *eip712_typed_data)
            data["signature"] = signature

        if data:
            kwargs.update({"data": JsonPayload(data)})

        return args


@dataclass
class Item:
    name: str | Callable[[tuple[str, URL], dict[str, Any]], str]
    func: Any


class DynamicNameSelector:
    @staticmethod
    def okx(args: tuple[str, URL], kwargs: dict[str, Any]) -> str:
        headers: CIMultiDict = kwargs["headers"]

        if "x-simulated-trading" in headers:
            if headers["x-simulated-trading"] == "1":
                return "okx_demo"
        return "okx"


class Hosts:
    # NOTE: yarl.URL.host is also allowed to be None. So, for brevity, relax the type check on the `items` key.
    items: dict[str | None, Item] = {
        "api.bybit.com": Item("bybit", Auth.bybit),
        "api.bytick.com": Item("bybit", Auth.bybit),
        "api-demo.bybit.com": Item("bybit_demo", Auth.bybit),
        "api-testnet.bybit.com": Item("bybit_testnet", Auth.bybit),
        "api.binance.com": Item("binance", Auth.binance),
        "api-gcp.binance.com": Item("binance", Auth.binance),
        "api1.binance.com": Item("binance", Auth.binance),
        "api2.binance.com": Item("binance", Auth.binance),
        "api3.binance.com": Item("binance", Auth.binance),
        "api4.binance.com": Item("binance", Auth.binance),
        "testnet.binance.vision": Item("binancespot_testnet", Auth.binance),
        "fapi.binance.com": Item("binance", Auth.binance),
        "dapi.binance.com": Item("binance", Auth.binance),
        "testnet.binancefuture.com": Item("binancefuture_testnet", Auth.binance),
        "api.bitflyer.com": Item("bitflyer", Auth.bitflyer),
        "api.coin.z.com": Item("gmocoin", Auth.gmocoin),
        "api.bitbank.cc": Item("bitbank", Auth.bitbank),
        "www.bitmex.com": Item("bitmex", Auth.bitmex),
        "testnet.bitmex.com": Item("bitmex_testnet", Auth.bitmex),
        "api.phemex.com": Item("phemex", Auth.phemex),
        "vapi.phemex.com": Item("phemex", Auth.phemex),
        "testnet-api.phemex.com": Item("phemex_testnet", Auth.phemex),
        "coincheck.com": Item("coincheck", Auth.coincheck),
        "www.okx.com": Item(DynamicNameSelector.okx, Auth.okx),
        "aws.okx.com": Item(DynamicNameSelector.okx, Auth.okx),
        "api.bitget.com": Item("bitget", Auth.bitget),
        "www.mexc.com": Item("mexc", Auth.mexc_v2),
        "contract.mexc.com": Item("mexc", Auth.mexc_v2),
        "api.mexc.com": Item("mexc", Auth.mexc_v3),
        "api.kucoin.com": Item("kucoin", Auth.kucoin),
        "api-futures.kucoin.com": Item("kucoin", Auth.kucoin),
        "www.okcoin.jp": Item("okj", Auth.okj),
        "api-cloud.bittrade.co.jp": Item("bittrade", Auth.bittrade),
        "api.hyperliquid.xyz": Item("hyperliquid", Auth.hyperliquid),
        "api.hyperliquid-testnet.xyz": Item("hyperliquid_testnet", Auth.hyperliquid),
    }


class PassphraseRequiredExchanges:
    items = {"okx", "bitget", "kucoin", "okj"}
