"""Дополнительные тесты для увеличения покрытия."""

import json
from datetime import datetime

import pandas as pd

from src import reports, services

# === Дополнительные тесты для reports.py ===


def test_get_date_range_invalid_date():
    """Тест с невалидной датой."""
    start, end = reports._get_date_range("invalid-date")
    # Должна вернуться текущая дата
    assert (end - start).days == 90


def test_spending_by_category_missing_columns():
    """Тест с отсутствующими колонками."""
    df = pd.DataFrame({"other": [1, 2, 3]})
    result = reports.spending_by_category(df, "Продукты")
    assert len(result) == 0


def test_spending_by_weekday_missing_columns():
    """Тест с отсутствующими колонками."""
    df = pd.DataFrame({"other": [1, 2, 3]})
    result = reports.spending_by_weekday(df)
    assert len(result) == 0


def test_spending_by_workday_missing_columns():
    """Тест с отсутствующими колонками."""
    df = pd.DataFrame({"other": [1, 2, 3]})
    result = reports.spending_by_workday(df)
    assert len(result) == 0


def test_spending_by_weekday_missing_sum():
    """Тест с отсутствующей колонкой Сумма."""
    df = pd.DataFrame({"Дата операции": [datetime.now()]})
    result = reports.spending_by_weekday(df)
    assert len(result) == 0


def test_spending_by_workday_missing_sum():
    """Тест с отсутствующей колонкой Сумма."""
    df = pd.DataFrame({"Дата операции": [datetime.now()]})
    result = reports.spending_by_workday(df)
    assert len(result) == 0


def test_save_report_with_invalid_path():
    """Тест сохранения в недоступный путь."""
    import logging

    logging.basicConfig(level=logging.ERROR)

    @reports.save_report("/invalid/path/file.json")
    def get_data():
        return {"test": "data"}

    result = get_data()
    assert result["test"] == "data"


# === Дополнительные тесты для services.py ===


def test_cashback_categories_invalid_date():
    """Тест с невалидной датой."""
    transactions = [
        {"Дата операции": "invalid", "Категория": "Еда", "Кэшбэк": 10},
        {"Дата операции": "15.01.2022", "Категория": "Еда", "Кэшбэк": 20},
    ]
    result = services.cashback_categories(transactions, 2022, 1)
    assert result["Еда"] == 20.0


def test_cashback_categories_missing_keys():
    """Тест с отсутствующими ключами."""
    transactions = [
        {"other": "value"},
        {"Дата операции": "15.01.2022", "Кэшбэк": 10},  # нет Категории
        {"Категория": "Еда", "Кэшбэк": 10},  # нет Даты
    ]
    result = services.cashback_categories(transactions, 2022, 1)
    assert result == {}


def test_investment_bank_invalid_month():
    """Тест с невалидным месяцем."""
    result = services.investment_bank("invalid", [], limit=10)
    assert result == 0.0


def test_investment_bank_missing_date():
    """Тест с отсутствующей датой."""
    transactions = [
        {"Сумма операции": -100, "Сумма операции с округлением": 101},
    ]
    result = services.investment_bank("2022-01", transactions, limit=10)
    assert result == 0.0


def test_investment_bank_invalid_date_format():
    """Тест с невалидным форматом даты."""
    transactions = [
        {"Дата операции": "invalid", "Сумма операции": -100, "Сумма операции с округлением": 101},
    ]
    result = services.investment_bank("2022-01", transactions, limit=10)
    assert result == 0.0


def test_simple_search_missing_keys():
    """Тест с отсутствующими ключами."""
    transactions = [
        {"other": "value"},
    ]
    result = services.simple_search("test", transactions)
    data = json.loads(result)
    assert data == []


def test_find_phone_transactions_missing_keys():
    """Тест с отсутствующими ключами."""
    transactions = [
        {"other": "value"},
    ]
    result = services.find_phone_transactions(transactions)
    data = json.loads(result)
    assert data == []


def test_find_person_transfers_missing_keys():
    """Тест с отсутствующими ключами."""
    transactions = [
        {"other": "value"},
    ]
    result = services.find_person_transfers(transactions)
    data = json.loads(result)
    assert data == []
