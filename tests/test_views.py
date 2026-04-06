"""Тесты для модуля views."""

import json
from datetime import datetime, timedelta

import pandas as pd
import pytest

from src import views


@pytest.fixture
def sample_transactions():
    """Создает пример DataFrame с транзакциями."""
    dates = [
        datetime.now() - timedelta(days=5),
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=20),
    ]
    data = {
        "Дата операции": dates,
        "Категория": ["Продукты", "Транспорт", "Продукты"],
        "Сумма": [1500.0, 500.0, 2000.0],
        "Описание": ["Магазин", "Метро", "Супермаркет"],
    }
    return pd.DataFrame(data)


# === Тесты для main_page ===
def test_main_page_success():
    """Тест главной страницы с корректной датой."""
    result = views.main_page("2024-06-15 12:30:45")
    data = json.loads(result)

    assert data["date"] == "2024-06-15"
    assert data["time"] == "12:30:45"
    assert "currency_rates" in data
    assert "stock_prices" in data


def test_main_page_invalid_date():
    """Тест главной страницы с некорректной датой."""
    result = views.main_page("invalid-date")
    data = json.loads(result)

    assert "date" in data
    assert "time" in data


# === Тесты для events_page ===
def test_events_page_week(sample_transactions):
    """Тест страницы событий за неделю."""
    result = views.events_page(sample_transactions, datetime.now().strftime("%Y-%m-%d"), "W")
    data = json.loads(result)

    assert data["period"] == "W"
    assert "total_spent" in data
    assert "total_transactions" in data
    assert "top_categories" in data


def test_events_page_month(sample_transactions):
    """Тест страницы событий за месяц."""
    result = views.events_page(sample_transactions, datetime.now().strftime("%Y-%m-%d"), "M")
    data = json.loads(result)

    assert data["period"] == "M"


def test_events_page_year(sample_transactions):
    """Тест страницы событий за год."""
    result = views.events_page(sample_transactions, datetime.now().strftime("%Y-%m-%d"), "Y")
    data = json.loads(result)

    assert data["period"] == "Y"


def test_events_page_all(sample_transactions):
    """Тест страницы событий за все время."""
    result = views.events_page(sample_transactions, datetime.now().strftime("%Y-%m-%d"), "ALL")
    data = json.loads(result)

    assert data["period"] == "ALL"


def test_events_page_empty_transactions():
    """Тест страницы событий с пустым DataFrame."""
    df = pd.DataFrame()
    result = views.events_page(df, "2024-06-15", "M")
    data = json.loads(result)

    assert data["total_spent"] == 0
    assert data["total_transactions"] == 0


def test_events_page_invalid_date(sample_transactions):
    """Тест страницы событий с некорректной датой."""
    result = views.events_page(sample_transactions, "invalid-date", "M")
    data = json.loads(result)

    assert "period" in data
