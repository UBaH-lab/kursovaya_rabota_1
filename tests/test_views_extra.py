"""Дополнительные тесты для views.py."""

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src import views


def test_main_page_currency_error():
    """Тест обработки ошибки получения курсов валют."""
    with patch("src.views.get_currency_rates", side_effect=Exception("API error")):
        with patch("src.views.get_stock_prices", return_value={"AAPL": 150}):
            result = views.main_page("2022-01-15 10:00:00")
            data = json.loads(result)
            assert data["currency_rates"] == {}


def test_main_page_stock_error():
    """Тест обработки ошибки получения цен акций."""
    with patch("src.views.get_currency_rates", return_value={"USD": 75}):
        with patch("src.views.get_stock_prices", side_effect=Exception("API error")):
            result = views.main_page("2022-01-15 10:00:00")
            data = json.loads(result)
            assert data["stock_prices"] == {}


def test_events_page_year_period():
    """Тест периода Y (год)."""
    df = pd.DataFrame(
        {
            "Дата операции": [datetime(2022, 1, 10), datetime(2022, 1, 15)],
            "Сумма": [-100, -200],
            "Категория": ["Еда", "Транспорт"],
        }
    )

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "Y")
            data = json.loads(result)
            assert data["period"] == "Y"


def test_events_page_missing_category():
    """Тест с отсутствующей колонкой Категория."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Сумма": [-100]})

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["top_categories"] == {}


def test_events_page_missing_sum():
    """Тест с отсутствующей колонкой Сумма."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Категория": ["Еда"]})

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["total_spent"] == 0.0


def test_events_page_currency_error():
    """Тест обработки ошибки курсов валют в events_page."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Сумма": [-100]})

    with patch("src.views.get_currency_rates", side_effect=Exception("API error")):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["currency_rates"] == {}


def test_events_page_stock_error():
    """Тест обработки ошибки цен акций в events_page."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Сумма": [-100]})

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", side_effect=Exception("API error")):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["stock_prices"] == {}
