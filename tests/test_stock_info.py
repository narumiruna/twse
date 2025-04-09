import json

import httpx
import pytest
import respx

from twse.stock_info import URL
from twse.stock_info import get_stock_info


@pytest.mark.parametrize(
    "symbols,testdata",
    [
        (["2317"], "tests/testdata/2317_limit_down.json"),
        (["006208"], "tests/testdata/006208_limit_down_after_hour.json"),
        (["0050", "006208", "2330", "2412", "2539"], "tests/testdata/0050_006208_2330_2412_2539.json"),
    ],
)
def test_get_stock_info(symbols, testdata) -> None:
    with open(testdata) as file:
        mock_response = json.load(file)

    with respx.mock as mock:
        mock_route = mock.get(URL).mock(return_value=httpx.Response(200, json=mock_response))
        resp = get_stock_info(symbols)

        assert mock_route.called

        for stock in resp.msg_array:
            assert stock.symbol in symbols


def test_query_stock_info_input_validation():
    """Test input validation for stock codes."""
    with pytest.raises(ValueError):
        get_stock_info("")  # Empty string

    with pytest.raises(ValueError):
        get_stock_info([])  # Empty list

    with pytest.raises(TypeError):
        get_stock_info(None)  # None value
