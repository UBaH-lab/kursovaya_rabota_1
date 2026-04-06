"""Тесты для непокрытых строк."""

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src import utils, views

# === UTILS.PY - строка 66 (except в get_currency_rates) ===


def test_get_currency_rates_exception():
    """Тест обработки исключения в get_currency_rates - строка 66."""
    with patch("requests.get", side_effect=Exception("Network error")):
        result = utils.get_currency_rates(["USD", "EUR"])
        assert result == {"USD": None, "EUR": None}


# === UTILS.PY - строки 141-142 (декабрь в get_month_range) ===


def test_get_month_range_december_2023():
    """Тест декабря 2023 - строки 141-142."""
    start, end = utils.get_month_range("2023-12-15")
    assert start == "2023-12-01"
    assert end == "2023-12-31"


def test_get_month_range_december_datetime():
    """Тест декабря с datetime."""
    dt = datetime(2023, 12, 15)
    start, end = utils.get_month_range(dt)
    assert start == "2023-12-01"
    assert end == "2023-12-31"


# === VIEWS.PY - строка 23 (Доброй ночи) ===


def test_get_greeting_night_22():
    """Тест ночи 22:00 - строка 23."""
    dt = datetime(2022, 1, 15, 22, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


def test_get_greeting_night_23():
    """Тест ночи 23:00."""
    dt = datetime(2022, 1, 15, 23, 30, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


def test_get_greeting_night_midnight():
    """Тест полуночи."""
    dt = datetime(2022, 1, 15, 0, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


def test_get_greeting_night_3am():
    """Тест 3 часа ночи."""
    dt = datetime(2022, 1, 15, 3, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


# === VIEWS.PY - строка 96 (pd.Timestamp) ===


def test_main_page_top_transactions_with_timestamp():
    """Тест с pd.Timestamp датой."""
    ts = pd.Timestamp("2022-01-10")
    transactions = [{"Дата операции": ts, "Сумма платежа": -1000, "Категория": "Еда", "Описание": "Тест"}]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert len(data["top_transactions"]) == 1
                    assert data["top_transactions"][0]["date"] == "10.01.2022"


# === VIEWS.PY - строка 188 ===


def test_events_page_empty_result():
    """Тест events_page с пустым результатом - строка 188."""
    df = pd.DataFrame()

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["total_transactions"] == 0
