from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse


def _channel_prefix(channel: str) -> str:
    return channel.split(":", 1)[0]


def _channel_suffix(channel: str) -> str | None:
    if ":" not in channel:
        return None
    return channel.split(":", 1)[1]


def _channel_market_id(channel: str) -> int | None:
    suffix = _channel_suffix(channel)
    if suffix is None:
        return None
    try:
        return int(suffix)
    except ValueError:
        return None


def _is_zero_size(value: Any) -> bool:
    try:
        return float(value) == 0.0
    except (TypeError, ValueError):
        return False


class LighterDataStore(DataStoreCollection):
    """DataStoreCollection for Lighter.

    https://apidocs.lighter.xyz/docs/websocket-reference
    """

    def _init(self) -> None:
        self._create("order_book", datastore_class=OrderBook)
        self._create("ticker", datastore_class=Ticker)
        self._create("market_stats", datastore_class=MarketStats)
        self._create("trade", datastore_class=Trade)
        self._create("account_all", datastore_class=ChannelStore)
        self._create("account_market", datastore_class=ChannelStore)
        self._create("user_stats", datastore_class=ChannelStore)
        self._create("account_tx", datastore_class=ChannelStore)
        self._create("account_all_orders", datastore_class=ChannelStore)
        self._create("height", datastore_class=ChannelStore)
        self._create("pool_data", datastore_class=ChannelStore)
        self._create("pool_info", datastore_class=ChannelStore)
        self._create("notification", datastore_class=ChannelStore)
        self._create("account_orders", datastore_class=AccountOrders)
        self._create("account_all_trades", datastore_class=ChannelStore)
        self._create("account_all_positions", datastore_class=ChannelStore)
        self._create("spot_market_stats", datastore_class=SpotMarketStats)
        self._create("account_all_assets", datastore_class=ChannelStore)
        self._create("account_spot_avg_entry_prices", datastore_class=ChannelStore)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = msg.get("channel")
        if not isinstance(channel, str):
            return

        prefix = _channel_prefix(channel)

        if prefix == "order_book":
            self.order_book._onmessage(msg)
        elif prefix == "ticker":
            self.ticker._onmessage(msg)
        elif prefix == "market_stats":
            self.market_stats._onmessage(msg)
        elif prefix == "trade":
            self.trade._onmessage(msg)
        elif prefix == "account_all":
            self.account_all._onmessage(msg)
        elif prefix == "account_market":
            self.account_market._onmessage(msg)
        elif prefix == "user_stats":
            self.user_stats._onmessage(msg)
        elif prefix == "account_tx":
            self.account_tx._onmessage(msg)
        elif prefix == "account_all_orders":
            self.account_all_orders._onmessage(msg)
        elif prefix == "height":
            self.height._onmessage(msg)
        elif prefix == "pool_data":
            self.pool_data._onmessage(msg)
        elif prefix == "pool_info":
            self.pool_info._onmessage(msg)
        elif prefix == "notification":
            self.notification._onmessage(msg)
        elif prefix == "account_orders":
            self.account_orders._onmessage(msg)
        elif prefix == "account_all_trades":
            self.account_all_trades._onmessage(msg)
        elif prefix == "account_all_positions":
            self.account_all_positions._onmessage(msg)
        elif prefix == "spot_market_stats":
            self.spot_market_stats._onmessage(msg)
        elif prefix == "account_all_assets":
            self.account_all_assets._onmessage(msg)
        elif prefix == "account_spot_avg_entry_prices":
            self.account_spot_avg_entry_prices._onmessage(msg)

    @property
    def order_book(self) -> OrderBook:
        return self._get("order_book", OrderBook)

    @property
    def ticker(self) -> Ticker:
        return self._get("ticker", Ticker)

    @property
    def market_stats(self) -> MarketStats:
        return self._get("market_stats", MarketStats)

    @property
    def trade(self) -> Trade:
        return self._get("trade", Trade)

    @property
    def account_all(self) -> ChannelStore:
        return self._get("account_all", ChannelStore)

    @property
    def account_market(self) -> ChannelStore:
        return self._get("account_market", ChannelStore)

    @property
    def user_stats(self) -> ChannelStore:
        return self._get("user_stats", ChannelStore)

    @property
    def account_tx(self) -> ChannelStore:
        return self._get("account_tx", ChannelStore)

    @property
    def account_all_orders(self) -> ChannelStore:
        return self._get("account_all_orders", ChannelStore)

    @property
    def height(self) -> ChannelStore:
        return self._get("height", ChannelStore)

    @property
    def pool_data(self) -> ChannelStore:
        return self._get("pool_data", ChannelStore)

    @property
    def pool_info(self) -> ChannelStore:
        return self._get("pool_info", ChannelStore)

    @property
    def notification(self) -> ChannelStore:
        return self._get("notification", ChannelStore)

    @property
    def account_orders(self) -> AccountOrders:
        return self._get("account_orders", AccountOrders)

    @property
    def account_all_trades(self) -> ChannelStore:
        return self._get("account_all_trades", ChannelStore)

    @property
    def account_all_positions(self) -> ChannelStore:
        return self._get("account_all_positions", ChannelStore)

    @property
    def spot_market_stats(self) -> SpotMarketStats:
        return self._get("spot_market_stats", SpotMarketStats)

    @property
    def account_all_assets(self) -> ChannelStore:
        return self._get("account_all_assets", ChannelStore)

    @property
    def account_spot_avg_entry_prices(self) -> ChannelStore:
        return self._get("account_spot_avg_entry_prices", ChannelStore)


class ChannelStore(DataStore):
    _KEYS = ["channel"]

    def _onmessage(self, msg: Item) -> None:
        self._insert([msg])


class AccountOrders(ChannelStore):
    _KEYS = ["account", "channel"]


class OrderBook(DataStore):
    _KEYS = ["market_id", "side", "price"]

    def _init(self) -> None:
        self._last_nonce: dict[int, int] = {}

    def _onmessage(self, msg: Item) -> None:
        channel = msg.get("channel")
        if not isinstance(channel, str):
            return

        market_id = _channel_market_id(channel)
        order_book = msg.get("order_book")
        if market_id is None or not isinstance(order_book, dict):
            return

        nonce = order_book.get("nonce")
        begin_nonce = order_book.get("begin_nonce")
        last_nonce = self._last_nonce.get(market_id)
        if last_nonce is None or begin_nonce != last_nonce:
            self._delete(self.find({"market_id": market_id}))

        offset = msg.get("offset", order_book.get("offset"))
        timestamp = msg.get("timestamp")

        for side in ("asks", "bids"):
            insert_data: list[Item] = []
            delete_data: list[Item] = []

            for level in order_book.get(side, []):
                if not isinstance(level, dict):
                    continue

                item = {
                    "market_id": market_id,
                    "channel": channel,
                    "side": side,
                    "price": level.get("price"),
                    "size": level.get("size"),
                    "offset": offset,
                    "nonce": nonce,
                    "begin_nonce": begin_nonce,
                    "timestamp": timestamp,
                }

                if _is_zero_size(level.get("size")):
                    delete_data.append(item)
                else:
                    insert_data.append(item)

            if delete_data:
                self._delete(delete_data)
            if insert_data:
                self._insert(insert_data)

        if isinstance(nonce, int):
            self._last_nonce[market_id] = nonce

    def sorted(
        self, *, market_id: int | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        query = None if market_id is None else {"market_id": market_id}
        return self._sorted("side", "asks", "bids", "price", query=query, limit=limit)


class Ticker(DataStore):
    _KEYS = ["market_id"]

    def _onmessage(self, msg: Item) -> None:
        channel = msg.get("channel")
        ticker = msg.get("ticker")
        if not isinstance(channel, str) or not isinstance(ticker, dict):
            return

        market_id = _channel_market_id(channel)
        if market_id is None:
            return

        item = {
            "market_id": market_id,
            "channel": channel,
            "nonce": msg.get("nonce"),
            **ticker,
        }
        self._insert([item])


class MarketStats(DataStore):
    _KEYS = ["market_id"]
    _FIELD = "market_stats"

    def _onmessage(self, msg: Item) -> None:
        channel = msg.get("channel")
        market_stats = msg.get(self._FIELD)
        if not isinstance(channel, str) or not isinstance(market_stats, dict):
            return

        items: list[Item] = []
        if channel.endswith(":all"):
            for key, value in market_stats.items():
                if not isinstance(value, dict):
                    continue
                market_id = value.get("market_id")
                if not isinstance(market_id, int):
                    market_id = int(key)
                item = {
                    "market_id": market_id,
                    "channel": channel,
                    **value,
                }
                items.append(item)
        else:
            market_id = market_stats.get("market_id", _channel_market_id(channel))
            if not isinstance(market_id, int):
                return
            items.append({"market_id": market_id, "channel": channel, **market_stats})

        if items:
            self._insert(items)


class SpotMarketStats(MarketStats):
    _FIELD = "spot_market_stats"


class Trade(DataStore):
    _KEYS = ["market_id", "trade_id"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        channel = msg.get("channel")
        trades = msg.get("trades")
        if not isinstance(channel, str):
            return

        if isinstance(trades, dict):
            trade_items = [trades]
        elif isinstance(trades, list):
            trade_items = [item for item in trades if isinstance(item, dict)]
        else:
            return

        items: list[Item] = []
        market_id = _channel_market_id(channel)
        for trade in trade_items:
            item = {"channel": channel, **trade}
            if market_id is not None:
                item.setdefault("market_id", market_id)
            items.append(item)

        if items:
            self._insert(items)
