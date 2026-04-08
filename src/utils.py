"""Утилиты для работы с данными транзакций."""

import json
from datetime import datetime
from typing import Any

import pandas as pd
import requests


def load_transactions(filepath: str = "data/operations.xlsx") -> list[dict[str, Any]]:
    """Загружает транзакции из Excel-файла.

    Args:
        filepath: Путь к файлу с транзакциями.

    Returns:
        Список словарей с транзакциями.
    """
    df = pd.read_excel(filepath)

    # Удаляем строки со статусом, отличным от OK
    df = df[df["Статус"] == "OK"]

    # Преобразуем в список словарей
    transactions = df.to_dict(orient="records")

    return transactions


def load_user_settings(filepath: str = "data/user_settings.json") -> dict[str, Any]:
    """Загружает пользовательские настройки из JSON-файла.

    Args:
        filepath: Путь к файлу с настройками.

    Returns:
        Словарь с настройками пользователя.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_currency_rates(currencies: list[str]) -> dict[str, float]:
    """Получает курсы валют от API.

    Args:
        currencies: Список кодов валют (например, ["USD", "EUR"]).

    Returns:
        Словарь с курсами валют {код: курс к рублю}.
    """
    # Используем API курсов валют
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rates = {}
        for currency in currencies:
            if currency in data["Valute"]:
                rates[currency] = data["Valute"][currency]["Value"]
            else:
                rates[currency] = None

        return rates
    except Exception:
        # Если API недоступен, возвращаем None
        return {currency: None for currency in currencies}


def get_stock_prices(stocks: list[str]) -> dict[str, float]:
    """Получает цены акций от Yahoo Finance API.

    Args:
        stocks: Список тикеров акций (например, ["AAPL", "GOOGL"]).

    Returns:
        Словарь с ценами акций {тикер: цена}.
    """
    import yfinance as yf
    
    result = {}
    
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="1d")
            if not hist.empty:
                result[stock] = round(hist["Close"].iloc[-1], 2)
            else:
                result[stock] = None
        except Exception:
            result[stock] = None
    
    return result


def format_date(date_str: str | datetime) -> str:
    """Форматирует дату в строку YYYY-MM-DD.

    Args:
        date_str: Строка с датой или объект datetime.

    Returns:
        Отформатированная строка даты.
    """
    if isinstance(date_str, datetime):
        return date_str.strftime("%Y-%m-%d")

    # Если строка в формате "31.12.2021" или "31.12.2021 16:44:00"
    try:
        # Пробуем разные форматы
        for fmt in ["%d.%m.%Y %H:%M:%S", "%d.%m.%Y", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(str(date_str), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return str(date_str)
    except Exception:
        return str(date_str)


def get_month_range(date: str | datetime) -> tuple[str, str]:
    """Возвращает начало и конец месяца для указанной даты.

    Args:
        date: Дата в любом формате.

    Returns:
        Кортеж (начало_месяца, конец_месяца) в формате YYYY-MM-DD.
    """
    if isinstance(date, str):
        date = datetime.strptime(format_date(date), "%Y-%m-%d")

    start = date.replace(day=1)

    # Находим последний день месяца
    if date.month == 12:
        end = date.replace(day=31)
    else:
        next_month = date.replace(month=date.month + 1, day=1)
        end = next_month.replace(day=1) - pd.Timedelta(days=1)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
