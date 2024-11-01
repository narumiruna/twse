import pytest

from twse.stock_info import query_stock_info


def test_query_stock_info_success():
    """Test successful stock info query for TSMC (2330)."""
    response = query_stock_info("2330")

    # Verify response structure
    assert response.rtmessage == "OK"
    assert response.rtcode == "0000"
    assert len(response.msg_array) > 0

    # Verify TSMC stock data
    stock = response.msg_array[0]
    assert stock.symbol == "2330"  # Stock code
    assert stock.name == "台積電"  # Stock name
    assert stock.full_name == "台灣積體電路製造股份有限公司"  # Full company name
    assert stock.exchange == "tse"  # Exchange

    # Verify price and volume fields exist and are in correct format
    assert stock.last_price is not None  # Current price
    assert stock.accumulated_volume is not None  # Volume
    assert stock.open_price is not None  # Opening price
    assert stock.high_price is not None  # High price
    assert stock.low_price is not None  # Low price


def test_query_stock_info_multiple():
    """Test querying multiple stocks at once."""
    response = query_stock_info(["2330", "2317"])  # TSMC and Hon Hai

    assert response.rtmessage == "OK"
    assert len(response.msg_array) > 0

    # Verify we got data for both stocks
    stock_codes = {stock.symbol for stock in response.msg_array if stock.symbol}
    assert "2330" in stock_codes
    assert "2317" in stock_codes


def test_query_stock_info_invalid():
    """Test querying an invalid stock code."""
    response = query_stock_info("0000")  # Invalid stock code

    assert response.rtmessage == "OK"
    assert len(response.msg_array) > 0

    # Invalid stock entries should have minimal data
    stock = response.msg_array[1]  # Second entry is usually the invalid one
    assert stock.trade_volume == "-"
    assert stock.last_price == "-"
    assert not stock.symbol  # Empty string for invalid stock code


def test_query_stock_info_input_validation():
    """Test input validation for stock codes."""
    with pytest.raises(ValueError):
        query_stock_info("")  # Empty string

    with pytest.raises(ValueError):
        query_stock_info([])  # Empty list

    with pytest.raises(TypeError):
        query_stock_info(None)  # None value
