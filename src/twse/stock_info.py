from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from typing import Literal

import httpx
from loguru import logger
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic.alias_generators import to_camel

from .utils import save_json


class StockInfo(BaseModel):
    exchange_id: str | None = Field(None, validation_alias="@")
    trade_volume: float | None = Field(None, validation_alias="tv")
    price_spread: float | None = Field(None, validation_alias="ps")
    price_id: str | None = Field(None, validation_alias="pid")
    trade_price: float | None = Field(None, validation_alias="pz")
    best_price: float | None = Field(None, validation_alias="bp")
    final_volume: str | None = Field(None, validation_alias="fv")
    best_ask_price: str | None = Field(None, validation_alias="oa")
    best_bid_price: str | None = Field(None, validation_alias="ob")
    market_percent: float | None = Field(None, validation_alias="m%")
    caret: str | None = Field(None, validation_alias="^")
    key: str | None = None
    ask_prices: str | None = Field(None, validation_alias="a")
    bid_prices: str | None = Field(None, validation_alias="b")
    symbol: str | None = Field(None, validation_alias="c")
    hash_id: str | None = Field(None, validation_alias="#")
    trade_date: str | None = Field(None, validation_alias="d")
    price_change_percent: str | None = Field(None, validation_alias="%")
    ticker: str | None = Field(None, validation_alias="ch")
    timestamp: str | None = Field(None, validation_alias="tlong")
    order_time: str | None = Field(None, validation_alias="ot")
    ask_volumes: str | None = Field(None, validation_alias="f")
    bid_volumes: str | None = Field(None, validation_alias="g")
    intraday_price: float | None = Field(None, validation_alias="ip")
    market_time: str | None = Field(None, validation_alias="mt")
    open_volume: str | None = Field(None, validation_alias="ov")
    high_price: float | None = Field(None, validation_alias="h")
    index: str | None = Field(None, validation_alias="i")
    intraday_time: str | None = Field(None, validation_alias="it")
    open_price_z: str | None = Field(None, validation_alias="oz")
    low_price: float | None = Field(None, validation_alias="l")
    name: str | None = Field(None, validation_alias="n")
    open_price: float | None = Field(None, validation_alias="o")
    price: float | None = Field(None, validation_alias="p")
    exchange: Literal["tse", "otc"] | None = Field(None, validation_alias="ex")
    sequence: str | None = Field(None, validation_alias="s")
    time: str | None = Field(None, validation_alias="t")
    upper_limit: float | None = Field(None, validation_alias="u")
    accumulated_volume: float | None = Field(None, validation_alias="v")
    lower_limit: float | None = Field(None, validation_alias="w")
    full_name: str | None = Field(None, validation_alias="nf")
    prev_close: float | None = Field(None, validation_alias="y")
    last_price: float | None = Field(None, validation_alias="z")
    tick_sequence: str | None = Field(None, validation_alias="ts")

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

        # Filter out non-positive values
        asks = [a for a in asks if a > 0]
        bids = [b for b in bids if b > 0]

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

        price = self.last_price or self.trade_price or self.mid_price

        if self.prev_close and price:
            lines.append(f"Prev Close: `{self.prev_close:,.2f}`")

            net_change = (price / self.prev_close - 1.0) * 100
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
