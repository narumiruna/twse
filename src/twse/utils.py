import json
from pathlib import Path


def save_json(obj: dict | list, f: str | Path) -> None:
    path = Path(f)
    if path.suffix != ".json":
        raise ValueError(f"File name must end with .json, got {path.suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as fp:
        json.dump(obj, fp, indent=2, ensure_ascii=False)


def to_alias(field_name: str) -> str:
    alias = {
        "exchange_id": "@",
        "trade_volume": "tv",
        "price_spread": "ps",
        "price_id": "pid",
        "trade_price": "pz",
        "best_price": "bp",
        "final_volume": "fv",
        "best_ask_price": "oa",
        "best_bid_price": "ob",
        "market_percent": "m%",
        "caret": "^",
        "ask_prices": "a",
        "bid_prices": "b",
        "symbol": "c",
        "hash_id": "#",
        "trade_date": "d",
        "price_change_percent": "%",
        "ticker": "ch",
        "timestamp": "tlong",
        "order_time": "ot",
        "ask_volumes": "f",
        "bid_volumes": "g",
        "intraday_price": "ip",
        "market_time": "mt",
        "open_volume": "ov",
        "high_price": "h",
        "index": "i",
        "intraday_time": "it",
        "open_price_z": "oz",
        "low_price": "l",
        "name": "n",
        "open_price": "o",
        "price": "p",
        "sequence": "s",
        "time": "t",
        "upper_limit": "u",
        "accumulated_volume": "v",
        "lower_limit": "w",
        "full_name": "nf",
        "prev_close": "y",
        "last_price": "z",
        "tick_sequence": "ts",
        "exchange": "ex",
    }
    return alias.get(field_name, field_name)
