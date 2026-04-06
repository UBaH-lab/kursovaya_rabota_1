"""Тесты для модуля utils."""

import json
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    format_date,
    get_currency_rates,
    get_month_range,
    get_stock_prices,
    load_transactions,
    load_user_settings,
)

# ===== Тесты для load_transactions =====


def test_load_transactions_success(tmp_path):
    """Тест успешной загрузки транзакций."""
    # Создаём тестовый Excel файл
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2022", "02.01.2022"],
            "Статус": ["OK", "OK"],
            "Сумма операции": [-100, -200],
            "Категория": ["Еда", "Транспорт"],
        }
    )

    filepath = tmp_path / "test_operations.xlsx"
    df.to_excel(filepath, index=False)

    # Загружаем
    transactions = load_transactions(str(filepath))

    assert len(transactions) == 2
    assert transactions[0]["Категория"] == "Еда"
    assert transactions[1]["Сумма операции"] == -200


def test_load_transactions_filter_status(tmp_path):
    """Тест фильтрации по статусу OK."""
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2022", "02.01.2022", "03.01.2022"],
            "Статус": ["OK", "FAILED", "OK"],
            "Сумма операции": [-100, -200, -300],
            "Категория": ["Еда", "Транспорт", "Еда"],
        }
    )

    filepath = tmp_path / "test_operations.xlsx"
    df.to_excel(filepath, index=False)

    transactions = load_transactions(str(filepath))

    # Должны остаться только OK
    assert len(transactions) == 2
    assert all(t["Статус"] == "OK" for t in transactions)


# ===== Тесты для load_user_settings =====


def test_load_user_settings_success(tmp_path):
    """Тест успешной загрузки настроек."""
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}

    filepath = tmp_path / "settings.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(settings, f)

    result = load_user_settings(str(filepath))

    assert result == settings
    assert result["user_currencies"] == ["USD", "EUR"]


def test_load_user_settings_file_not_found():
    """Тест обработки отсутствующего файла."""
    with pytest.raises(FileNotFoundError):
        load_user_settings("nonexistent.json")


# ===== Тесты для get_currency_rates =====


@patch("src.utils.requests.get")
def test_get_currency_rates_success(mock_get):
    """Тест успешного получения курсов валют."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Valute": {
            "USD": {"Value": 75.5},
            "EUR": {"Value": 85.2},
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    rates = get_currency_rates(["USD", "EUR"])

    assert rates["USD"] == 75.5
    assert rates["EUR"] == 85.2


@patch("src.utils.requests.get")
def test_get_currency_rates_api_error(mock_get):
    """Тест обработки ошибки API."""
    mock_get.side_effect = Exception("API Error")

    rates = get_currency_rates(["USD", "EUR"])

    assert rates["USD"] is None
    assert rates["EUR"] is None


# ===== Тесты для get_stock_prices =====


def test_get_stock_prices_known_stocks():
    """Тест получения цен известных акций."""
    prices = get_stock_prices(["AAPL", "GOOGL"])

    assert prices["AAPL"] is not None
    assert prices["GOOGL"] is not None
    assert isinstance(prices["AAPL"], float)


def test_get_stock_prices_unknown_stock():
    """Тест обработки неизвестного тикера."""
    prices = get_stock_prices(["UNKNOWN"])

    assert prices["UNKNOWN"] is None


# ===== Тесты для format_date =====


def test_format_date_from_string():
    """Тест форматирования строки даты."""
    result = format_date("31.12.2021")
    assert result == "2021-12-31"


def test_format_date_from_datetime():
    """Тест форматирования объекта datetime."""
    dt = datetime(2022, 5, 15)
    result = format_date(dt)
    assert result == "2022-05-15"


def test_format_date_with_time():
    """Тест форматирования даты со временем."""
    result = format_date("31.12.2021 16:44:00")
    assert result == "2021-12-31"


# ===== Тесты для get_month_range =====


def test_get_month_range_middle():
    """Тест получения диапазона месяца (середина года)."""
    start, end = get_month_range("15.06.2022")

    assert start == "2022-06-01"
    assert end == "2022-06-30"


def test_get_month_range_february():
    """Тест февраля (28 дней)."""
    start, end = get_month_range("15.02.2022")

    assert start == "2022-02-01"
    assert end == "2022-02-28"


def test_get_month_range_december():
    """Тест декабря (31 день)."""
    start, end = get_month_range("15.12.2022")

    assert start == "2022-12-01"
    assert end == "2022-12-31"


def test_get_month_range_from_datetime():
    """Тест с объектом datetime."""
    dt = datetime(2022, 3, 15)
    start, end = get_month_range(dt)

    assert start == "2022-03-01"
    assert end == "2022-03-31"
