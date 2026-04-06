"""Тесты для модуля services."""

import json


from src.services import (
    cashback_categories,
    find_person_transfers,
    find_phone_transactions,
    investment_bank,
    simple_search,
)

# ===== Тесты для cashback_categories =====


def test_cashback_categories_success():
    """Тест успешного расчёта кэшбэка."""
    transactions = [
        {"Дата операции": "15.01.2022 10:00:00", "Категория": "Супермаркеты", "Кэшбэк": 50},
        {"Дата операции": "20.01.2022 15:30:00", "Категория": "Супермаркеты", "Кэшбэк": 30},
        {"Дата операции": "25.01.2022 18:00:00", "Категория": "Транспорт", "Кэшбэк": 20},
        {"Дата операции": "10.02.2022 12:00:00", "Категория": "Супермаркеты", "Кэшбэк": 100},
    ]

    result = cashback_categories(transactions, 2022, 1)

    assert "Супермаркеты" in result
    assert result["Супермаркеты"] == 80.0
    assert result["Транспорт"] == 20.0


def test_cashback_categories_empty():
    """Тест с пустым списком."""
    result = cashback_categories([], 2022, 1)
    assert result == {}


def test_cashback_categories_with_none():
    """Тест обработки None значений."""
    transactions = [
        {"Дата операции": "15.01.2022", "Категория": "Еда", "Кэшбэк": None},
        {"Дата операции": "16.01.2022", "Категория": "Еда", "Кэшбэк": 25},
    ]

    result = cashback_categories(transactions, 2022, 1)

    assert result["Еда"] == 25.0


# ===== Тесты для investment_bank =====


def test_investment_bank_success():
    """Тест расчёта инвесткопилки."""
    transactions = [
        {"Дата операции": "15.01.2022", "Сумма операции": -100.50, "Сумма операции с округлением": 101},
        {"Дата операции": "20.01.2022", "Сумма операции": -200.30, "Сумма операции с округлением": 201},
    ]

    result = investment_bank("2022-01", transactions, limit=10)

    assert result == 1.2  # 0.50 + 0.70


def test_investment_bank_wrong_month():
    """Тест с другим месяцем."""
    transactions = [
        {"Дата операции": "15.02.2022", "Сумма операции": -100.50, "Сумма операции с округлением": 101},
    ]

    result = investment_bank("2022-01", transactions, limit=10)

    assert result == 0.0


def test_investment_bank_limit():
    """Тест лимита округления."""
    transactions = [
        {"Дата операции": "15.01.2022", "Сумма операции": -100.90, "Сумма операции с округлением": 105},  # diff = 4.10
        {"Дата операции": "16.01.2022", "Сумма операции": -200.10, "Сумма операции с округлением": 201},  # diff = 0.90
    ]

    result = investment_bank("2022-01", transactions, limit=2)

    assert result == 0.9  # только 0.90 проходит лимит


# ===== Тесты для simple_search =====


def test_simple_search_by_description():
    """Тест поиска по описанию."""
    transactions = [
        {"Описание": "Магнит", "Категория": "Супермаркеты"},
        {"Описание": "Перекрёсток", "Категория": "Супермаркеты"},
        {"Описание": "Яндекс Такси", "Категория": "Транспорт"},
    ]

    result = simple_search("Магнит", transactions)
    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Описание"] == "Магнит"


def test_simple_search_by_category():
    """Тест поиска по категории."""
    transactions = [
        {"Описание": "Магнит", "Категория": "Супермаркеты"},
        {"Описание": "Перекрёсток", "Категория": "Супермаркеты"},
        {"Описание": "Яндекс Такси", "Категория": "Транспорт"},
    ]

    result = simple_search("Супермаркеты", transactions)
    data = json.loads(result)

    assert len(data) == 2


def test_simple_search_no_results():
    """Тест без результатов."""
    transactions = [
        {"Описание": "Магнит", "Категория": "Супермаркеты"},
    ]

    result = simple_search("Несуществующее", transactions)
    data = json.loads(result)

    assert len(data) == 0


def test_simple_search_empty_query():
    """Тест с пустым запросом."""
    transactions = [{"Описание": "Магнит"}]

    result = simple_search("", transactions)
    data = json.loads(result)

    assert data == []


# ===== Тесты для find_phone_transactions =====


def test_find_phone_transactions_found():
    """Тест поиска телефонов."""
    transactions = [
        {"Описание": "Перевод на +7 999 123-45-67"},
        {"Описание": "Оплата в магазине"},
        {"Описание": "Перевод 8(926)555-44-33"},
    ]

    result = find_phone_transactions(transactions)
    data = json.loads(result)

    assert len(data) == 2


def test_find_phone_transactions_not_found():
    """Тест когда телефонов нет."""
    transactions = [
        {"Описание": "Оплата в магазине"},
        {"Описание": "Покупка товара"},
    ]

    result = find_phone_transactions(transactions)
    data = json.loads(result)

    assert len(data) == 0


# ===== Тесты для find_person_transfers =====


def test_find_person_transfers_by_category():
    """Тест поиска по категории."""
    transactions = [
        {"Описание": "Перевод", "Категория": "Переводы"},
        {"Описание": "Покупка", "Категория": "Супермаркеты"},
        {"Описание": "SBP перевод", "Категория": "Другое"},
    ]

    result = find_person_transfers(transactions)
    data = json.loads(result)

    assert len(data) == 2


def test_find_person_transfers_by_keywords():
    """Тест поиска по ключевым словам."""
    transactions = [
        {"Описание": "Перевод физлицу", "Категория": "Другое"},
        {"Описание": "Оплата СБП", "Категория": "Другое"},
        {"Описание": "Покупка товара", "Категория": "Супермаркеты"},
    ]

    result = find_person_transfers(transactions)
    data = json.loads(result)

    assert len(data) == 2


def test_find_person_transfers_empty():
    """Тест с пустым списком."""
    result = find_person_transfers([])
    data = json.loads(result)

    assert len(data) == 0
