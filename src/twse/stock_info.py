import time

import httpx
from pydantic import BaseModel
from pydantic import Field


class StockInfo(BaseModel):
    exchange_id: str | None = Field(None, validation_alias="@")
    tv: str | None = None
    ps: str | None = None
    pid: str | None = None
    pz: str | None = None
    bp: str | None = None
    fv: str | None = None
    oa: str | None = None
    ob: str | None = None
    m_percent: str | None = Field(None, validation_alias="m%")
    caret: str | None = Field(None, validation_alias="^")
    key: str | None = None
    a: str | None = None
    b: str | None = None
    c: str | None = None
    hash_id: str | None = Field(None, validation_alias="#")
    d: str | None = None
    percent: str | None = Field(None, validation_alias="%")
    ch: str | None = None
    tlong: str | None = None
    ot: str | None = None
    f: str | None = None
    g: str | None = None
    ip: str | None = None
    mt: str | None = None
    ov: str | None = None
    h: str | None = None
    i: str | None = None
    it: str | None = None
    oz: str | None = None
    low_price: str | None = Field(None, validation_alias="l")
    n: str | None = None
    o: str | None = None
    p: str | None = None
    ex: str | None = None
    s: str | None = None
    t: str | None = None
    u: str | None = None
    v: str | None = None
    w: str | None = None
    nf: str | None = None
    y: str | None = None
    z: str | None = None
    ts: str | None = None


class QueryTime(BaseModel):
    sys_date: str = Field(validation_alias="sysDate")
    stock_info_item: int = Field(validation_alias="stockInfoItem")
    stock_info: int = Field(validation_alias="stockInfo")
    session_str: str = Field(validation_alias="sessionStr")
    sys_time: str = Field(validation_alias="sysTime")
    show_chart: bool = Field(validation_alias="showChart")
    session_from_time: int = Field(validation_alias="sessionFromTime")
    session_latest_time: int = Field(validation_alias="sessionLatestTime")


class StockInfoResponse(BaseModel):
    msg_array: list[StockInfo] = Field(validation_alias="msgArray")
    referer: str
    user_delay: int = Field(validation_alias="userDelay")
    rtcode: str
    query_time: QueryTime = Field(validation_alias="queryTime")
    rtmessage: str
    ex_key: str = Field(validation_alias="exKey")
    cached_alive: int = Field(validation_alias="cachedAlive")


def build_ex_ch(symbols: list[str]) -> str:
    strings = []

    for symbol in symbols:
        if symbol.isdigit():
            strings += [f"tse_{symbol}.tw"]
            strings += [f"otc_{symbol}.tw"]
        else:
            strings += [symbol]

    return "|".join(strings)


def query_stock_info(symbols: str | list[str]) -> StockInfoResponse:
    if isinstance(symbols, str):
        symbols = [symbols]

    params = {
        "ex_ch": build_ex_ch(symbols),
        "json": 1,
        "delay": 0,
        "_": int(time.time() * 1000),
    }

    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"

    resp = httpx.get(url, params=params)
    resp.raise_for_status()

    return StockInfoResponse.model_validate(resp.json())
