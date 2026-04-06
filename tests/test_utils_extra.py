"""Дополнительные тесты для utils.py."""

from datetime import datetime
from unittest.mock import patch

import requests

from src import utils


def test_get_currency_rates_request_exception():
    """Тест обработки RequestException."""
    with patch("src.utils.requests.get", side_effect=requests.RequestException("Error")):
        result = utils.get_currency_rates(["USD"])
        assert result == {"USD": None}


def test_get_currency_rates_timeout():
    """Тест обработки таймаута."""
    with patch("src.utils.requests.get", side_effect=requests.Timeout("Timeout")):
        result = utils.get_currency_rates(["USD"])
        assert result == {"USD": None}


def test_get_month_range_december_branch():
    """Тест ветки декабря."""
    start, end = utils.get_month_range(datetime(2022, 12, 15))
    assert start == "2022-12-01"
    assert end == "2022-12-31"


def test_get_month_range_december_from_string():
    """Тест декабря из строки."""
    start, end = utils.get_month_range("15.12.2022")
    assert start == "2022-12-01"
    assert end == "2022-12-31"
