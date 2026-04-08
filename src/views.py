"""Модуль с функциями для генерации JSON-ответов для веб-страниц."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from src.utils import get_currency_rates, get_stock_prices, load_transactions, load_user_settings

logger = logging.getLogger(__name__)


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = dt.hour
    if 4 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def main_page(date_time: str) -> str:
    """Функция для главной страницы.

    Args:
        date_time: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS

    Returns:
        JSON-ответ с данными для главной страницы
    """
    # Парсим дату
    try:
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.now()

    # Загружаем пользовательские настройки
    try:
        settings = load_user_settings()
        currencies = settings.get("user_currencies", ["USD", "EUR"])
        stocks = settings.get("user_stocks", ["AAPL", "GOOGL", "MSFT", "TSLA"])
    except Exception:
        currencies = ["USD", "EUR"]
        stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]

    # Загружаем транзакции
    try:
        transactions = load_transactions()
    except Exception:
        transactions = []

    # Фильтруем транзакции за текущий месяц (с начала месяца по указанную дату)
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    df = pd.DataFrame(transactions)
    if "Дата операции" in df.columns and len(df) > 0:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= dt)]

        # Определяем колонку суммы
        sum_col = "Сумма платежа" if "Сумма платежа" in df.columns else "Сумма" if "Сумма" in df.columns else None

        # Данные по картам
        cards_data = []
        if "Номер карты" in df.columns and sum_col:
            # Фильтруем только расходы (отрицательные суммы)
            expenses_df = df[df[sum_col] < 0]

            for card_num, group in expenses_df.groupby("Номер карты"):
                total_spent = float(abs(group[sum_col].sum()))
                cashback = total_spent / 100  # 1 рубль на каждые 100 рублей

                cards_data.append(
                    {
                        "last_digits": str(card_num).replace("*", ""),
                        "total_spent": round(total_spent, 2),
                        "cashback": round(cashback, 2),
                    }
                )

        # Топ-5 транзакций
        top_transactions = []
        if sum_col:
            # Сортируем по убыванию абсолютной величины
            df_sorted = df.reindex(df[sum_col].abs().sort_values(ascending=False).index)
            top_5 = df_sorted.head(5)

            for _, row in top_5.iterrows():
                date_str = row.get("Дата операции", "")
                if pd.notna(date_str):
                    if isinstance(date_str, pd.Timestamp):
                        date_str = date_str.strftime("%d.%m.%Y")
                    else:
                        try:
                            date_str = pd.to_datetime(date_str).strftime("%d.%m.%Y")
                        except Exception:
                            date_str = str(date_str)
                else:
                    date_str = ""

                top_transactions.append(
                    {
                        "date": date_str,
                        "amount": float(row.get(sum_col, 0)),
                        "category": str(row.get("Категория", "")),
                        "description": str(row.get("Описание", "")),
                    }
                )
    else:
        cards_data = []
        top_transactions = []
        sum_col = None

    # Курсы валют
    try:
        currency_rates_dict = get_currency_rates(currencies)
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        currency_rates_dict = {}

    # Цены акций
    try:
        stock_prices_dict = get_stock_prices(stocks)
    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        stock_prices_dict = {}

    result = {
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M:%S"),
        "greeting": get_greeting(dt),
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates_dict,
        "stock_prices": stock_prices_dict,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


def events_page(transactions: Any, date: str, period: str = "M") -> str:
    """Функция для страницы событий.

    Args:
        transactions: DataFrame или список транзакций
        date: Строка с датой в формате YYYY-MM-DD
        period: Период (W - неделя, M - месяц, Y - год, ALL - все данные)

    Returns:
        JSON-ответ с данными для страницы событий
    """
    # Парсим дату
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        dt = datetime.now()

    # Определяем начальную дату в зависимости от периода
    if period == "W":
        # Неделя
        start_date = dt - timedelta(days=dt.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "M":
        # Месяц - с начала месяца
        start_date = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "Y":
        # Год - с начала года
        start_date = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        # ALL - все данные
        start_date = datetime.min

    # Загружаем пользовательские настройки
    try:
        settings = load_user_settings()
        currencies = settings.get("user_currencies", ["USD", "EUR"])
        stocks = settings.get("user_stocks", ["AAPL", "GOOGL", "MSFT", "TSLA"])
    except Exception:
        currencies = ["USD", "EUR"]
        stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]

    # Преобразуем в DataFrame если нужно
    if isinstance(transactions, pd.DataFrame):
        df = transactions.copy()
    else:
        df = pd.DataFrame(transactions) if transactions else pd.DataFrame()

    # Определяем колонку суммы
    sum_col = "Сумма платежа" if "Сумма платежа" in df.columns else "Сумма" if "Сумма" in df.columns else None

    if "Дата операции" in df.columns and len(df) > 0:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= dt)]

        # РАСХОДЫ
        expenses_df = df[df[sum_col] < 0] if sum_col and len(df) > 0 else pd.DataFrame()

        total_expenses = int(abs(expenses_df[sum_col].sum())) if len(expenses_df) > 0 else 0

        # Основные расходы - топ-7 категорий + Остальное
        main_expenses = {}
        if "Категория" in expenses_df.columns and sum_col:
            category_totals = expenses_df.groupby("Категория")[sum_col].apply(lambda x: abs(x).sum())
            category_totals = category_totals.sort_values(ascending=False)

            for cat, amount in category_totals.items():
                main_expenses[cat] = int(amount)

        # Переводы и наличные
        transfers_cash = []
        if "Категория" in expenses_df.columns and sum_col:
            transfer_categories = ["Наличные", "Переводы"]
            for cat in transfer_categories:
                cat_df = expenses_df[expenses_df["Категория"] == cat]
                if len(cat_df) > 0:
                    transfers_cash.append({"category": cat, "amount": int(abs(cat_df[sum_col].sum()))})
            # Сортируем по убыванию
            transfers_cash.sort(key=lambda x: int(str(x["amount"])), reverse=True)

        # ПОСТУПЛЕНИЯ
        income_df = df[df[sum_col] > 0] if sum_col and len(df) > 0 else pd.DataFrame()

        total_income = int(income_df[sum_col].sum()) if len(income_df) > 0 else 0

        # Поступления по категориям
        main_income = []
        if "Категория" in income_df.columns and sum_col:
            category_totals = income_df.groupby("Категория")[sum_col].sum()
            category_totals = category_totals.sort_values(ascending=False)

            main_income = [{"category": cat, "amount": int(amount)} for cat, amount in category_totals.items()]

        total_transactions = len(df)
        total_spent = total_expenses
    else:
        total_expenses = 0
        main_expenses = {}
        transfers_cash = []
        total_income = 0
        main_income = []
        total_spent = 0
        total_transactions = 0

    # Курсы валют
    try:
        currency_rates_dict = get_currency_rates(currencies)
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        currency_rates_dict = {}

    # Цены акций
    try:
        stock_prices_dict = get_stock_prices(stocks)
    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        stock_prices_dict = {}

    result = {
        "period": period,
        "total_spent": total_spent,
        "total_transactions": total_transactions,
        "top_categories": main_expenses,
        "expenses": {
            "total_amount": total_expenses,
            "main": [{"category": k, "amount": v} for k, v in main_expenses.items()],
            "transfers_and_cash": transfers_cash,
        },
        "income": {"total_amount": total_income, "main": main_income},
        "currency_rates": currency_rates_dict,
        "stock_prices": stock_prices_dict,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
