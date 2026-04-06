"""Главный модуль приложения для анализа транзакций."""

import json
from datetime import datetime
from typing import Any

import pandas as pd

from src import reports, services, views


def load_user_settings() -> dict[str, Any]:
    """Загружает пользовательские настройки из файла."""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}


def print_section(title: str) -> None:
    """Выводит заголовок раздела."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print("=" * 50)


def main() -> None:
    """Точка входа в приложение."""
    print_section("АНАЛИЗ ТРАНЗАКЦИЙ")

    # Загружаем настройки
    settings = load_user_settings()
    current_date = datetime.now()
    date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")

    # === VIEWS: Главная страница ===
    print_section("Главная страница (views.main_page)")
    try:
        result = views.main_page(date_str)
        data = json.loads(result)
        print(f"\nПриветствие: {data.get('greeting', 'N/A')}")
        print(f"Всего транзакций: {data.get('total_transactions', 0)}")
        print("Топ-5 транзакций:")
        for i, t in enumerate(data.get("top_transactions", [])[:5], 1):
            print(f"  {i}. {t.get('date', 'N/A')} | {t.get('amount', 0):.2f} RUB | {t.get('category', 'N/A')}")
        print("\nКурсы валют:")
        for r in data.get("currency_rates", []):
            print(f"  {r.get('currency', 'N/A')}: {r.get('rate', 'N/A')}")
        print("\nАкции:")
        for s in data.get("stock_prices", []):
            print(f"  {s.get('stock', 'N/A')}: ")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === VIEWS: Страница событий ===
    print_section("Страница событий (views.events_page)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = views.events_page(df, current_date.strftime("%Y-%m-%d"), "M")
        data = json.loads(result)
        print(f"\nРасходы: {data.get('expenses', {}).get('total_amount', 0)} RUB")
        print(f"Поступления: {data.get('income', {}).get('total_amount', 0)} RUB")
        print("\nОсновные расходы:")
        for cat in data.get("expenses", {}).get("main", [])[:5]:
            print(f"  {cat.get('category', 'N/A')}: {cat.get('amount', 0)} RUB")
        print("\nПереводы и наличные:")
        for cat in data.get("expenses", {}).get("transfers_and_cash", []):
            print(f"  {cat.get('category', 'N/A')}: {cat.get('amount', 0)} RUB")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === SERVICES: Выгодные категории ===
    print_section("Выгодные категории (services.profitable_categories)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = services.profitable_categories(df, current_date.year, current_date.month)
        data = json.loads(result)
        print("\nКешбэк по категориям:")
        for category, amount in data.items():
            print(f"  {category}: {amount:.2f} RUB")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === SERVICES: Инвесткопилка ===
    print_section("Инвесткопилка (services.investment_bank)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        month_str = current_date.strftime("%Y-%m")
        transactions = df.to_dict("records")
        result = services.investment_bank(month_str, transactions, 50)
        print(f"\nСумма в инвесткопилке за {month_str}: {result:.2f} RUB")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === SERVICES: Поиск ===
    print_section("Поиск (services.simple_search)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = services.simple_search(df, "супермаркет")
        data = json.loads(result)
        print(f"\nНайдено транзакций: {len(data)}")
        for t in data[:3]:
            print(f"  {t.get('Дата операции', 'N/A')} | {t.get('Категория', 'N/A')}")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === SERVICES: Поиск телефонов ===
    print_section("Поиск телефонов (services.search_phone_numbers)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = services.search_phone_numbers(df)
        data = json.loads(result)
        print(f"\nНайдено транзакций: {len(data)}")
        for t in data[:3]:
            print(f"  {t.get('Дата операции', 'N/A')} | {t.get('Описание', 'N/A')}")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === SERVICES: Поиск переводов физлицам ===
    print_section("Поиск переводов физлицам (services.search_person_transfers)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = services.search_person_transfers(df)
        data = json.loads(result)
        print(f"\nНайдено переводов: {len(data)}")
        for t in data[:3]:
            print(f"  {t.get('Дата операции', 'N/A')} | {t.get('Описание', 'N/A')}")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === REPORTS: Траты по категории ===
    print_section("Траты по категории (reports.spending_by_category)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = reports.spending_by_category(df, "Супермаркеты")
        print("\nТраты в категории 'Супермаркеты':")
        if isinstance(result, pd.DataFrame):
            print(result.to_string())
        else:
            print(result)
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === REPORTS: Траты по дням недели ===
    print_section("Траты по дням недели (reports.spending_by_weekday)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = reports.spending_by_weekday(df)
        print("\nСредние траты по дням недели:")
        if isinstance(result, pd.DataFrame):
            print(result.to_string())
        else:
            print(result)
    except Exception as e:
        print(f"  Ошибка: {e}")

    # === REPORTS: Траты в рабочий/выходной ===
    print_section("Траты: рабочий vs выходной (reports.spending_by_workday)")
    try:
        df = pd.read_excel("data/operations.xlsx")
        result = reports.spending_by_workday(df)
        print("\nСредние траты:")
        if isinstance(result, pd.DataFrame):
            print(result.to_string())
        else:
            print(result)
    except Exception as e:
        print(f"  Ошибка: {e}")

    # Используем настройки для вывода
    print_section("Настройки пользователя")
    print(f"\nВалюты: {settings.get('user_currencies', [])}")
    print(f"Акции: {settings.get('user_stocks', [])}")

    print_section("АНАЛИЗ ЗАВЕРШЁН")


if __name__ == "__main__":
    main()
