from __future__ import annotations

import re
import time
from typing import Any

import httpx
from loguru import logger
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


def escape_markdown(text: str | None) -> str:
    """Escape special characters for Telegram MarkdownV2 format.

    Args:
        text: Text to escape, can be None

    Returns:
        Escaped text string, or empty string if input is None
    """
    if text is None:
        return ""

    pattern = r"([_*\[\]()~`>#+=|{}.!-])"
    return re.sub(pattern, r"\\\1", text)


class StockInfo(BaseModel):
    """Real-time stock information from TWSE."""

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
    exchange: str | None = Field(None, validation_alias="ex")  # TSE or OTC
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

    def _get_mid_price(self) -> float:
        """Calculate mid price from best ask and bid prices."""
        if not self.ask_prices or not self.bid_prices:
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
        """Format stock information in Telegram MarkdownV2 format."""
        if not self.symbol:
            return ""

        open_price = escape_markdown(f"{self.open_price:,.2f}")
        high_price = escape_markdown(f"{self.high_price:,.2f}")
        low_price = escape_markdown(f"{self.low_price:,.2f}")

        lines = [
            f"📊 *{escape_markdown(self.name)} \\({escape_markdown(self.symbol)}\\)*",
            f"Open: `{open_price}`",
            f"High: `{high_price}`",
            f"Low: `{low_price}`",
        ]

        if self.trade_price:
            lines.append(f"Trade Price: `{self.trade_price:,.2f}`")

        mid_price = self._get_mid_price()
        if mid_price:
            lines.append(f"Mid Price: `{mid_price:,.2f}`")

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
    """Query time information from TWSE."""

    sys_date: str = Field(validation_alias="sysDate")
    stock_info_item: int = Field(validation_alias="stockInfoItem")
    stock_info: int = Field(validation_alias="stockInfo")
    session_str: str = Field(validation_alias="sessionStr")
    sys_time: str = Field(validation_alias="sysTime")
    show_chart: bool = Field(validation_alias="showChart")
    session_from_time: int = Field(validation_alias="sessionFromTime")
    session_latest_time: int = Field(validation_alias="sessionLatestTime")


class StockInfoResponse(BaseModel):
    """Response from TWSE stock information API."""

    msg_array: list[StockInfo] = Field(validation_alias="msgArray")
    referer: str | None = None
    user_delay: int | None = Field(None, validation_alias="userDelay")
    rtcode: str | None = None
    query_time: QueryTime = Field(validation_alias="queryTime")
    rtmessage: str | None = None
    ex_key: str | None = Field(None, validation_alias="exKey")
    cached_alive: int | None = Field(None, validation_alias="cachedAlive")

    def pretty_repr(self) -> str:
        """Format response in Telegram MarkdownV2 format."""
        if not self.msg_array:
            return "*No stock information available*"

        result = []
        for stock in self.msg_array:
            if stock_info := stock.pretty_repr():
                result.append(stock_info)

        return "\n\n".join(result)


def build_ex_ch(symbols: list[str]) -> str:
    """Build exchange channel string for API request."""
    strings = []
    for symbol in symbols:
        if symbol.isdigit():
            strings.extend([f"tse_{symbol}.tw", f"otc_{symbol}.tw"])
        else:
            strings.append(symbol)
    return "|".join(strings)


def query_stock_info(symbols: str | list[str]) -> StockInfoResponse:
    """Query real-time stock information from TWSE.

    Args:
        symbols: Stock symbol(s) to query. Can be a single symbol string or list of symbols.

    Returns:
        StockInfoResponse containing the queried stock information.

    Raises:
        httpx.HTTPError: If the API request fails.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    params: dict[str, Any] = {
        "ex_ch": build_ex_ch(symbols),
        "json": 1,
        "delay": 0,
        "_": int(time.time() * 1000),
    }

    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    resp = httpx.get(url, params=params)
    resp.raise_for_status()
    import json

    with open("info.json", "w") as fp:
        json.dump(resp.json(), fp, indent=2, ensure_ascii=False)

    return StockInfoResponse.model_validate(resp.json())
