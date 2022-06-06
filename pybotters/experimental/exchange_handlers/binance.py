from typing import Any
import aiohttp
from pyee.asyncio import AsyncIOEventEmitter


class BinanceWebSocketHandler:
    def __init__(self) -> None:
        self.response = AsyncIOEventEmitter()
        self.stream = AsyncIOEventEmitter()

    def __call__(self, data: Any, ws: aiohttp.ClientWebSocketResponse) -> None:
        if isinstance(data, dict):
            if "id" in data:
                self.response.emit("message", data, ws)
            else:
                if "e" in data:
                    self.stream.emit(data["e"], data, ws)
                elif "stream" in data:
                    if isinstance(data["data"], dict):
                        self.stream.emit(data["data"]["e"], data["data"], ws)
                    elif isinstance(data["data"], list):
                        for item in data["data"]:
                            self.stream.emit(item["e"], item, ws)
        elif isinstance(data, list):
            for item in data:
                self.stream.emit(item["e"], item, ws)


class BinanceDataStoreManager:
    def __init__(self) -> None:
        self.create("trade", datastore_class=BinanceTrade)

        self.wshander = BinanceWebSocketHandler()
        self.wshander.stream.add_listener("trade", self["trade"])

    @property
    def trade(self) -> "BinanceTrade":
        return self["trade"]

    def __call__(self, data: Any, ws: aiohttp.ClientWebSocketResponse) -> None:
        return self.wshander

    def create(self, name, datastore_class) -> None:
        return


class BinanceTrade:
    def __init__(self) -> None:
        self.store = "DataStore()"
