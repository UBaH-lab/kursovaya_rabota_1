"""Тесты для модуля reports."""

import json
import os
import tempfile
from datetime import datetime, timedelta

import pandas as pd
import pytest

from src import reports


@pytest.fixture
def sample_transactions():
    """Создает пример DataFrame с транзакциями."""
    dates = [
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=20),
        datetime.now() - timedelta(days=40),
        datetime.now() - timedelta(days=60),
        datetime.now() - timedelta(days=80),
    ]
    data = {
        "Дата операции": dates,
        "Категория": ["Продукты", "Транспорт", "Продукты", "Развлечения", "Продукты"],
        "Сумма": [1500.0, 500.0, 2000.0, 3000.0, 1000.0],
        "Описание": ["Магазин", "Метро", "Супермаркет", "Кино", "Рынок"],
    }
    return pd.DataFrame(data)


# === Тесты для _get_date_range ===
def test_get_date_range_with_date():
    """Тест получения диапазона дат с указанной датой."""
    start, end = reports._get_date_range("2024-06-15")
    assert end == datetime(2024, 6, 15)
    assert (end - start).days == 90


def test_get_date_range_without_date():
    """Тест получения диапазона дат без указанной даты."""
    start, end = reports._get_date_range()
    assert (end - start).days == 90


# === Тесты для spending_by_category ===
def test_spending_by_category_found(sample_transactions):
    """Тест поиска трат по категории."""
    result = reports.spending_by_category(sample_transactions, "Продукты")
    assert len(result) == 3
    assert all(result["Категория"] == "Продукты")


def test_spending_by_category_not_found(sample_transactions):
    """Тест поиска трат по несуществующей категории."""
    result = reports.spending_by_category(sample_transactions, "Несуществующая")
    assert len(result) == 0


def test_spending_by_category_with_date(sample_transactions):
    """Тест поиска трат по категории с указанием даты."""
    result = reports.spending_by_category(sample_transactions, "Продукты", "2024-01-15")
    assert len(result) == 0  # Все транзакции позже этой даты


# === Тесты для spending_by_weekday ===
def test_spending_by_weekday_success(sample_transactions):
    """Тест расчета средних трат по дням недели."""
    result = reports.spending_by_weekday(sample_transactions)
    assert "День недели" in result.columns
    assert "Средняя сумма" in result.columns


def test_spending_by_weekday_empty():
    """Тест с пустым DataFrame."""
    df = pd.DataFrame()
    result = reports.spending_by_weekday(df)
    assert len(result) == 0


# === Тесты для spending_by_workday ===
def test_spending_by_workday_success(sample_transactions):
    """Тест расчета средних трат по типу дня."""
    result = reports.spending_by_workday(sample_transactions)
    assert "Тип дня" in result.columns
    assert "Средняя сумма" in result.columns


def test_spending_by_workday_empty():
    """Тест с пустым DataFrame."""
    df = pd.DataFrame()
    result = reports.spending_by_workday(df)
    assert len(result) == 0


# === Тесты для save_report ===
def test_save_report_to_file():
    """Тест сохранения отчета в файл."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filename = f.name

    try:

        @reports.save_report(filename)
        def get_data():
            return {"result": "test"}

        get_data()
        assert os.path.exists(filename)

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["result"] == "test"
    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_save_report_dataframe():
    """Тест сохранения DataFrame в файл."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filename = f.name

    try:

        @reports.save_report(filename)
        def get_dataframe():
            return pd.DataFrame({"col": [1, 2, 3]})

        get_dataframe()
        assert os.path.exists(filename)
    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_save_report_no_filename():
    """Тест декоратора без имени файла."""

    @reports.save_report()
    def get_data():
        return {"result": "test"}

    result = get_data()
    assert result["result"] == "test"
