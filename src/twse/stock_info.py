"""Taiwan Stock Exchange (TWSE) real-time stock information API client."""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel
from pydantic import Field


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
    trade_volume: str | None = Field(None, validation_alias="tv")
    price_spread: str | None = Field(None, validation_alias="ps")
    price_id: str | None = Field(None, validation_alias="pid")
    trade_price: str | None = Field(None, validation_alias="pz")
    best_price: str | None = Field(None, validation_alias="bp")
    final_volume: str | None = Field(None, validation_alias="fv")
    best_ask_price: str | None = Field(None, validation_alias="oa")
    best_bid_price: str | None = Field(None, validation_alias="ob")
    market_percent: str | None = Field(None, validation_alias="m%")
    caret: str | None = Field(None, validation_alias="^")
    key: str | None = None
    ask_prices: str | None = Field(None, validation_alias="a")  # "_" separated string
    bid_prices: str | None = Field(None, validation_alias="b")  # "_" separated string
    symbol: str | None = Field(None, validation_alias="c")
    hash_id: str | None = Field(None, validation_alias="#")
    trade_date: str | None = Field(None, validation_alias="d")
    price_change_percent: str | None = Field(None, validation_alias="%")
    ticker: str | None = Field(None, validation_alias="ch")
    timestamp: str | None = Field(None, validation_alias="tlong")
    order_time: str | None = Field(None, validation_alias="ot")
    ask_volumes: str | None = Field(None, validation_alias="f")  # "_" separated string
    bid_volumes: str | None = Field(None, validation_alias="g")  # "_" separated string
    intraday_price: str | None = Field(None, validation_alias="ip")
    market_time: str | None = Field(None, validation_alias="mt")
    open_volume: str | None = Field(None, validation_alias="ov")
    high_price: str | None = Field(None, validation_alias="h")
    index: str | None = Field(None, validation_alias="i")
    intraday_time: str | None = Field(None, validation_alias="it")
    open_price_z: str | None = Field(None, validation_alias="oz")
    low_price: str | None = Field(None, validation_alias="l")
    name: str | None = Field(None, validation_alias="n")
    open_price: str | None = Field(None, validation_alias="o")
    price: str | None = Field(None, validation_alias="p")
    exchange: str | None = Field(None, validation_alias="ex")  # TSE or OTC
    sequence: str | None = Field(None, validation_alias="s")
    time: str | None = Field(None, validation_alias="t")
    upper_limit: str | None = Field(None, validation_alias="u")
    accumulated_volume: str | None = Field(None, validation_alias="v")
    lower_limit: str | None = Field(None, validation_alias="w")
    full_name: str | None = Field(None, validation_alias="nf")
    prev_close: str | None = Field(None, validation_alias="y")
    last_price: str | None = Field(None, validation_alias="z")
    tick_sequence: str | None = Field(None, validation_alias="ts")

    def _parse_float(self, value: str | None) -> float:
        """Parse string to float, handling None and invalid values."""
        if not value or value == "-":
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _parse_int(self, value: str | None) -> int:
        """Parse string to integer, handling None and invalid values."""
        if not value or value == "-":
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _get_mid_price(self) -> float:
        """Calculate mid price from best ask and bid prices."""
        if not self.ask_prices or not self.bid_prices:
            return 0.0

        try:
            asks = self.ask_prices.split("_")
            bids = self.bid_prices.split("_")
            if not asks or not bids:
                return 0.0
            ask = self._parse_float(asks[0])
            bid = self._parse_float(bids[0])
            return (ask + bid) / 2.0
        except (IndexError, ValueError):
            return 0.0

    def _get_last_price(self) -> float:
        """Get last price from trade price or mid price."""
        trade_price = self._parse_float(self.trade_price)
        return trade_price if trade_price > 0 else self._get_mid_price()

    def pretty_repr(self) -> str:
        """Format stock information in Telegram MarkdownV2 format."""
        if not self.symbol:
            return ""

        last_price = self._get_last_price()
        prev_close = self._parse_float(self.prev_close)
        net_change = ((last_price / prev_close - 1.0) * 100) if prev_close > 0 else 0.0
        net_change_symbol = "🔺" if net_change > 0 else "🔻" if net_change < 0 else "⏸️"

        # Format numbers with escaped special characters
        open_price = escape_markdown(f"{self._parse_float(self.open_price):,.2f}")
        high_price = escape_markdown(f"{self._parse_float(self.high_price):,.2f}")
        low_price = escape_markdown(f"{self._parse_float(self.low_price):,.2f}")
        last_price_str = escape_markdown(f"{last_price:,.2f}")
        net_change_str = escape_markdown(f"{net_change:+.2f}%")
        volume = escape_markdown(f"{self._parse_int(self.accumulated_volume):,}")

        return (
            f"📊 *{escape_markdown(self.name)} \\({escape_markdown(self.symbol)}\\)*\n"
            f"Open: `{open_price}`\n"
            f"High: `{high_price}`\n"
            f"Low: `{low_price}`\n"
            f"Last: `{last_price_str}`\n"
            f"Change: {net_change_symbol} `{net_change_str}`\n"
            f"Volume: `{volume}`"
        )


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

        # Format date from YYYYMMDD to YYYY-MM-DD
        formatted_date = datetime.strptime(self.query_time.sys_date, "%Y%m%d").strftime("%Y-%m-%d")
        formatted_time = escape_markdown(f"{formatted_date} {self.query_time.sys_time}")

        result = [
            f"⏰ {formatted_time}",
        ]

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

    return StockInfoResponse.model_validate(resp.json())
