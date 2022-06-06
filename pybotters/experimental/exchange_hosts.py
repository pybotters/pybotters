from typing import Callable, Dict, Union, TYPE_CHECKING

from . import exchange_auth
from .helpers import BaseAuth

if TYPE_CHECKING:
    from .client_reqrep import ClientRequest

APIS_TABLE: Dict[str, BaseAuth] = {
    "bybit": exchange_auth.BybitAuth,
    "bybit_testnet": exchange_auth.BybitAuth,
    "binance": exchange_auth.BinanceAuth,
    "bitflyer": exchange_auth.bitFlyerAuth,
    "gmocoin": exchange_auth.GMOCoinAuth,
    "liquid": exchange_auth.LiquidAuth,
    "bitbank": exchange_auth.bitbankAuth,
    "ftx": exchange_auth.FTXAuth,
    "bitmex": exchange_auth.BitMEXAuth,
    "bitmex_testnet": exchange_auth.BitMEXAuth,
    "phemex": exchange_auth.PhemexAuth,
    "phemex_testnet": exchange_auth.PhemexAuth,
    "coincheck": exchange_auth.CoincheckAuth,
    "okx": exchange_auth.OKXAuth,
    "okx_demo": exchange_auth.OKXAuth,
    "bitget": exchange_auth.BitgetAuth,
    "mexc": exchange_auth.MEXCAuth,
}

HTTP_HOSTS: Dict[str, Union[str, Callable[["ClientRequest"], str]]] = {
    # bybit
    "api.bybit.com": "bybit",
    "api.bytick.com": "bybit",
    # bybit_testnet
    "api-testnet.bybit.com": "bybit_testnet",
    # binance
    "api.binance.com": "binance",
    "api1.binance.com": "binance",
    "api2.binance.com": "binance",
    "api3.binance.com": "binance",
    "fapi.binance.com": "binance",
    "dapi.binance.com": "binance",
    "vapi.binance.com": "binance",
    # binance_testnet
    "testnet.binancefuture.com": "binance_testnet",
    "testnet.binanceops.com": "binance_testnet",
    # bitflyer
    "api.bitflyer.com": "bitflyer",
    # gmocoin
    "api.coin.z.com": "gmocoin",
    # liquid
    "api.liquid.com": "liquid",
    # bitbank
    "api.bitbank.cc": "bitbank",
    # ftx
    "ftx.com": "ftx",
    # bitmex
    "www.bitmex.com": "bitmex",
    "ws.bitmex.com": "bitmex",
    # bitmex_testnet
    "testnet.bitmex.com": "bitmex_testnet",
    "ws.testnet.bitmex.com": "bitmex_testnet",
    # phemex
    "api.phemex.com": "phemex",
    "vapi.phemex.com": "phemex",
    # phemex_testnet
    "testnet-api.phemex.com": "phemex_testnet",
    # coincheck
    "coincheck.com": "coincheck",
    # okx
    "www.okx.com": (
        lambda req: "okx" if not exchange_auth.OKXAuth.isdemo(req) else "okx_demo"
    ),
    "aws.okx.com": (
        lambda req: "okx" if not exchange_auth.OKXAuth.isdemo(req) else "okx_demo"
    ),
    # bitget
    "api.bitget.com": "bitget",
    "capi.bitget.com": "bitget",
    # mexc
    "www.mexc.com": "mexc",
    "contract.mexc.com": "mexc",
    "api.mexc.com": "mexc",
}

WEBSOCKET_HOSTS: Dict[str, str] = {
    # bybit
    "stream.bybit.com": "bybit",
    "stream.bytick.com": "bybit",
    # bybit_testnet
    "stream-testnet.bybit.com": "bybit_testnet",
    # bitflyer
    "ws.lightstream.bitflyer.com": "bitflyer",
    # gmocoin
    "api.coin.z.com": "gmocoin",
    # liquid
    "tap.liquid.com": "liquid",
    # ftx
    "ftx.com": "ftx",
    # phemex
    "phemex.com": "phemex",
    # phemex_testnet
    "testnet.phemex": "phemex_testnet",
    # okx
    "ws.okx.com": "okx",
    "wsaws.okx.com": "okx",
    # okx_demo
    "wspap.okx.com": "okx_demo",
    # bitget
    "ws.bitget.com": "bitget",
    # mexc
    "contract.mexc.com": "mexc",
}

WSPING_HOSTS: Dict[str, str] = {
    # bybit
    "stream.bybit.com": "bybit",
    "stream.bytick.com": "bybit",
    # bybit_testnet
    "stream-testnet.bybit.com": "bybit_testnet",
    # liquid
    "tap.liquid.com": "liquid",
    # bitbank
    "stream.bitbank.cc": "bitbank",
    # ftx
    "ftx.com": "ftx",
    # phemex
    "phemex.com": "phemex",
    # phemex_testnet
    "testnet.phemex": "phemex_testnet",
    # okx
    "ws.okx.com": "okx",
    "wsaws.okx.com": "okx",
    # okx_demo
    "wspap.okx.com": "okx_demo",
    # bitget
    "ws.bitget.com": "bitget",
    # mexc
    "contract.mexc.com": "mexc",
}

WSRATELIMIT_HOSTS: Dict[str, str] = {
    # gmocoin
    "api.coin.z.com": "gmocoin",
    # binance
    "stream.binance.com": "binance",
}
