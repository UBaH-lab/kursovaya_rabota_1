"""Дополнительные тесты для полного покрытия views.py."""

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src import views


def test_get_greeting_night():
    """Тест ночного приветствия (22:00-04:00)."""
    # 23:00
    dt = datetime(2022, 1, 15, 23, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"

    # 03:00
    dt = datetime(2022, 1, 15, 3, 0, 0)
    assert views.get_greeting(dt) == "Доброй ночи"


def test_main_page_settings_error():
    """Тест ошибки загрузки настроек."""
    with patch("src.views.load_user_settings", side_effect=Exception("Settings error")):
        with patch("src.views.load_transactions", return_value=[]):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert "greeting" in data


def test_main_page_transactions_error():
    """Тест ошибки загрузки транзакций."""
    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", side_effect=Exception("Load error")):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert data["cards"] == []


def test_main_page_no_card_column():
    """Тест с отсутствующей колонкой Номер карты."""
    transactions = [{"Дата операции": "10.01.2022", "Сумма платежа": -100, "Категория": "Еда"}]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert data["cards"] == []


def test_main_page_date_string_conversion():
    """Тест конвертации строки даты в топ-транзакциях."""
    transactions = [{"Дата операции": "10.01.2022", "Сумма платежа": -1000, "Категория": "Еда", "Описание": "Тест"}]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert len(data["top_transactions"]) == 1
                    assert data["top_transactions"][0]["date"] == "10.01.2022"


def test_events_page_invalid_date():
    """Тест неверного формата даты в events_page."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Сумма": [-100]})

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "invalid-date", "M")
            data = json.loads(result)
            assert "period" in data


def test_events_page_all_period():
    """Тест периода ALL."""
    df = pd.DataFrame(
        {
            "Дата операции": [datetime(2020, 1, 10), datetime(2022, 1, 15)],
            "Сумма": [-100, -200],
            "Категория": ["Еда", "Транспорт"],
        }
    )

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "ALL")
            data = json.loads(result)
            assert data["period"] == "ALL"
            assert data["total_transactions"] == 2


def test_events_page_empty_result():
    """Тест с пустым результатом после фильтрации."""
    df = pd.DataFrame(
        {"Дата операции": [datetime(2021, 1, 10)], "Сумма": [-100], "Категория": ["Еда"]}  # Дата вне диапазона
    )

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["total_transactions"] == 0


def test_events_page_with_transfers():
    """Тест с переводами и наличными."""
    df = pd.DataFrame(
        {
            "Дата операции": [datetime(2022, 1, 10), datetime(2022, 1, 11)],
            "Сумма": [-500, -300],
            "Категория": ["Переводы", "Наличные"],
        }
    )

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert len(data["expenses"]["transfers_and_cash"]) == 2


def test_events_page_with_income():
    """Тест с поступлениями."""
    df = pd.DataFrame(
        {
            "Дата операции": [datetime(2022, 1, 10), datetime(2022, 1, 11)],
            "Сумма": [5000, 3000],
            "Категория": ["Зарплата", "Перевод"],
        }
    )

    with patch("src.views.get_currency_rates", return_value={}):
        with patch("src.views.get_stock_prices", return_value={}):
            result = views.events_page(df, "2022-01-15", "M")
            data = json.loads(result)
            assert data["income"]["total_amount"] == 8000


def test_events_page_settings_error():
    """Тест ошибки загрузки настроек в events_page."""
    df = pd.DataFrame({"Дата операции": [datetime(2022, 1, 10)], "Сумма": [-100]})

    with patch("src.views.load_user_settings", side_effect=Exception("Settings error")):
        with patch("src.views.get_currency_rates", return_value={}):
            with patch("src.views.get_stock_prices", return_value={}):
                result = views.events_page(df, "2022-01-15", "M")
                data = json.loads(result)
                assert "currency_rates" in data


def test_main_page_with_cards():
    """Тест с данными по картам."""
    transactions = [
        {"Дата операции": "10.01.2022", "Сумма платежа": -100, "Категория": "Еда", "Номер карты": "*1234"},
        {"Дата операции": "11.01.2022", "Сумма платежа": -200, "Категория": "Транспорт", "Номер карты": "*1234"},
        {"Дата операции": "12.01.2022", "Сумма платежа": -150, "Категория": "Еда", "Номер карты": "*5678"},
    ]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert len(data["cards"]) == 2


def test_main_page_multiple_transactions():
    """Тест с несколькими транзакциями для топ-5."""
    transactions = [
        {
            "Дата операции": f"{i:02d}.01.2022",
            "Сумма платежа": -i * 100,
            "Категория": f"Кат{i}",
            "Описание": f"Опис{i}",
        }
        for i in range(1, 8)  # 7 транзакций
    ]

    with patch("src.views.load_user_settings", return_value={}):
        with patch("src.views.load_transactions", return_value=transactions):
            with patch("src.views.get_currency_rates", return_value={}):
                with patch("src.views.get_stock_prices", return_value={}):
                    result = views.main_page("2022-01-15 10:00:00")
                    data = json.loads(result)
                    assert len(data["top_transactions"]) == 5
