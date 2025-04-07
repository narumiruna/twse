from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from typing import Literal

import httpx
from loguru import logger
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic.alias_generators import to_camel

from .utils import save_json
from .utils import to_alias


class StockInfo(BaseModel):
    model_config = ConfigDict(alias_generator=to_alias)

    exchange_id: str | None = None
    trade_volume: float | None = None
    price_spread: float | None = None
    price_id: str | None = None
    trade_price: float | None = None
    best_price: float | None = None
    final_volume: str | None = None
    best_ask_price: str | None = None
    best_bid_price: str | None = None
    market_percent: float | None = None
    caret: str | None = None
    key: str | None = None
    ask_prices: str | None = None
    bid_prices: str | None = None
    symbol: str | None = None
    hash_id: str | None = None
    trade_date: str | None = None
    price_change_percent: str | None = None
    ticker: str | None = None
    timestamp: str | None = None
    order_time: str | None = None
    ask_volumes: str | None = None
    bid_volumes: str | None = None
    intraday_price: float | None = None
    market_time: str | None = None
    open_volume: str | None = None
    high_price: float | None = None
    index: str | None = None
    intraday_time: str | None = None
    open_price_z: str | None = None
    low_price: float | None = None
    name: str | None = None
    open_price: float | None = None
    price: float | None = None
    exchange: Literal["tse", "otc"] | None = None
    sequence: str | None = None
    time: str | None = None
    upper_limit: float | None = None
    accumulated_volume: float | None = None
    lower_limit: float | None = None
    full_name: str | None = None
    prev_close: float | None = None
    last_price: float | None = None
    tick_sequence: str | None = None

    @field_validator(
        "trade_volume",
        "price_spread",
        "trade_price",
        "best_price",
        "market_percent",
        "intraday_price",
        "high_price",
        "low_price",
        "open_price",
        "price",
        "upper_limit",
        "accumulated_volume",
        "lower_limit",
        "prev_close",
        "last_price",
        mode="before",
    )
    @classmethod
    def convert_float(cls, value: str | None) -> float | None:
        if value is None:
            return 0.0

        if value == "-":
            return 0.0

        try:
            return float(value)
        except ValueError as e:
            logger.error("unable to convert {} to float: {}", value, e)
            return 0.0

    @property
    def mid_price(self) -> float:
        if self.ask_prices is None or self.bid_prices is None:
            return 0.0

        asks = [float(a) for a in self.ask_prices.split("_") if a and a != "-"]
        bids = [float(b) for b in self.bid_prices.split("_") if b and b != "-"]
        if len(asks) == 0 and len(bids) == 0:
            return 0.0
        elif len(asks) == 0:
            return max(bids)
        elif len(bids) == 0:
            return min(asks)
        else:
            return (max(bids) + min(asks)) / 2.0

    def pretty_repr(self) -> str:
        if not self.symbol:
            return ""

        lines = [
            f"📊 *{self.name} \\({self.symbol}\\)*",
            f"Open: `{self.open_price:,.2f}`",
            f"High: `{self.high_price:,.2f}`",
            f"Low: `{self.low_price:,.2f}`",
        ]

        if self.trade_price:
            lines.append(f"Trade Price: `{self.trade_price:,.2f}`")

        if self.mid_price:
            lines.append(f"Mid Price: `{self.mid_price:,.2f}`")

        if self.last_price:
            lines.append(f"Last Price: `{self.last_price:,.2f}`")

        if self.prev_close and self.last_price:
            lines.append(f"Prev Close: `{self.prev_close:,.2f}`")

            net_change = (self.last_price / self.prev_close - 1.0) * 100
            price_trend_icon = "🔺" if net_change > 0 else "🔻" if net_change < 0 else "⏸️"
            lines.append(f"Change: {price_trend_icon} `{net_change:+.2f}%`")

        if self.accumulated_volume:
            lines.append(f"Volume: `{self.accumulated_volume:,}`")

        return "\n".join(lines)


class QueryTime(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    sys_date: str
    stock_info_item: int
    stock_info: int
    session_str: str
    sys_time: str
    show_chart: bool
    session_from_time: int
    session_latest_time: int


class StockInfoResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    msg_array: list[StockInfo]
    referer: str | None = None
    user_delay: int | None = None
    rtcode: str | None = None
    query_time: QueryTime
    rtmessage: str | None = None
    ex_key: str | None = None
    cached_alive: int | None = None

    @field_validator("msg_array", mode="after")
    @classmethod
    def filter_empty(cls, value: list[StockInfo]) -> list[StockInfo]:
        return [stock for stock in value if stock.symbol and stock.name]

    def pretty_repr(self) -> str:
        if not self.msg_array:
            return "*No stock information available*"

        result = []
        for stock in self.msg_array:
            if stock_info := stock.pretty_repr():
                result.append(stock_info)

        return "\n\n".join(result)


def build_ex_ch(symbols: list[str]) -> str:
    strings = []
    for symbol in symbols:
        if symbol.isdigit():
            strings.extend([f"tse_{symbol}.tw", f"otc_{symbol}.tw"])
        else:
            strings.append(symbol)
    return "|".join(strings)


def build_params(symbols: str | list[str]) -> dict[str, Any]:
    if isinstance(symbols, str):
        symbols = [symbols]
    return {
        "ex_ch": build_ex_ch(symbols),
        "json": 1,
        "delay": 0,
        "_": int(time.time() * 1000),
    }


def get_stock_info(symbols: str | list[str]) -> StockInfoResponse:
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    resp = httpx.get(url, params=build_params(symbols))
    resp.raise_for_status()

    return StockInfoResponse.model_validate(resp.json())


def save_stock_info(symbols: str | list[str], output_json: str | Path) -> None:
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    resp = httpx.get(url, params=build_params(symbols))
    resp.raise_for_status()

    save_json(resp.json(), output_json)
