"""Финальные тесты для достижения максимального покрытия."""

import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd

from src import reports, utils, views

# === VIEWS.PY - строка 23 (ночь) ===


def test_get_greeting_night():
    """Тест ночи (22:00-04:00) - строка 23."""
    dt = datetime(2022, 1, 15, 22, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"

    dt = datetime(2022, 1, 15, 23, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"

    dt = datetime(2022, 1, 15, 0, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"

    dt = datetime(2022, 1, 15, 3, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


# === VIEWS.PY - строки 98-103 (NaN дата в топ-транзакциях) ===


def test_main_page_top_transactions_with_valid_date():
    """Тест топ-транзакций с валидной датой."""
    transactions = [
        {"Дата операции": "10.01.2022", "Сумма платежа": -5000, "Категория": "Еда", "Описание": "Ресторан"},
        {"Дата операции": "12.01.2022", "Сумма платежа": -3000, "Категория": "Транспорт", "Описание": "Такси"},
    ]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert len(data["top_transactions"]) == 2


# === VIEWS.PY - строка 188 (total_transactions = 0) ===


def test_events_page_empty_df():
    """Тест events_page с пустым DataFrame - строка 188."""
    df = pd.DataFrame()

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["total_transactions"] == 0


# === REPORTS.PY - строки 91-92 (сохранение отчёта) ===


def test_save_report_decorator():
    """Тест декоратора save_report с записью файла."""

    @reports.save_report("reports/test_report.json")
    def generate_test_report():
        return {"total": 100, "items": [1, 2, 3]}

    with patch("os.makedirs"):
        with patch("builtins.open", mock_open()):
            result = generate_test_report()
            assert result["total"] == 100


def test_save_report_decorator_with_dataframe():
    """Тест декоратора save_report с DataFrame."""

    @reports.save_report("reports/df_report.json")
    def generate_df_report():
        return pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    with patch("os.makedirs"):
        with patch("builtins.open", mock_open()):
            result = generate_df_report()
            assert len(result) == 2


def test_save_report_decorator_exception():
    """Тест обработки исключения в save_report."""

    @reports.save_report("reports/error.json")
    def generate_error():
        return {"data": "test"}

    with patch("os.makedirs", side_effect=PermissionError("No access")):
        result = generate_error()
        assert result["data"] == "test"


# === UTILS.PY - строка 66 (неизвестный формат даты) ===


def test_format_date_unknown_format():
    """Тест format_date с неизвестным форматом - строка 66."""
    # Передаём строку, которая не соответствует ни одному формату
    result = utils.format_date("15/01/2022")  # Формат DD/MM/YYYY
    assert result == "15/01/2022"  # Вернётся как есть


def test_format_date_partial_format():
    """Тест с частичным форматом даты."""
    result = utils.format_date("2022/01/15")
    assert result == "2022/01/15"


# === UTILS.PY - строки 122-123 (декабрь в get_month_range) ===


def test_get_month_range_december():
    """Тест декабря в get_month_range."""
    start, end = utils.get_month_range("2022-12-15")
    assert start == "2022-12-01"
    assert end == "2022-12-31"


def test_get_month_range_december_datetime():
    """Тест декабря с datetime объектом."""
    dt = datetime(2022, 12, 15)
    start, end = utils.get_month_range(dt)
    assert start == "2022-12-01"
    assert end == "2022-12-31"


def test_get_month_range_february():
    """Тест февраля (28 дней)."""
    start, end = utils.get_month_range("2022-02-15")
    assert start == "2022-02-01"
    assert end == "2022-02-28"


def test_get_month_range_february_leap():
    """Тест февраля високосного года."""
    start, end = utils.get_month_range("2024-02-15")
    assert start == "2024-02-01"
    assert end == "2024-02-29"
