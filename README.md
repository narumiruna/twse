# twse

A Python package for querying real-time stock information from Taiwan Stock Exchange (TWSE).

## Features

- Real-time stock data querying from TWSE
- Support for single or multiple stock symbols
- Comprehensive stock information including:
  - Current price, volume, and price changes
  - Open, high, low prices
  - Best bid/ask prices
  - Company information
- Formatted output suitable for display (including Telegram MarkdownV2 format)

## Installation

Requires Python 3.11 or higher.

```bash
pip install twse
```

## Usage

### Basic Usage

```python
from twse.stock_info import query_stock_info

# Query single stock (TSMC - 2330)
response = query_stock_info("2330")
print(response.pretty_repr())

# Query multiple stocks (TSMC - 2330 and Hon Hai - 2317)
response = query_stock_info(["2330", "2317"])
print(response.pretty_repr())
```

### Example Output

The `pretty_repr()` method formats the output in Telegram MarkdownV2 format:

```
⏰ 2024-03-21 14:30:00

📊 台積電 (2330)
Open: 735.00
High: 738.00
Low: 732.00
Last: 735.00
Change: 🔺 +0.68%
Volume: 15,234,567
```

### Stock Information Fields

The `StockInfo` class provides access to various fields:

- `symbol`: Stock symbol
- `name`: Stock name
- `full_name`: Full company name
- `last_price`: Current trading price
- `open_price`: Opening price
- `high_price`: High price
- `low_price`: Low price
- `accumulated_volume`: Trading volume
- `best_ask_price`: Best ask price
- `best_bid_price`: Best bid price
- And more...

## Development

### Setup

1. Clone the repository
2. Install dependencies using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv pip install -r requirements.txt
   ```

### Commands

- Run tests:
  ```bash
  make test
  ```
- Run linter:
  ```bash
  make lint
  ```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality. Install them with:

```bash
pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
