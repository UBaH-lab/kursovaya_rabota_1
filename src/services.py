"""Модуль с сервисными функциями."""

import json
import logging
import re
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


def cashback_categories(transactions: list[dict[str, Any]], year: int, month: int) -> dict[str, float]:
    """Возвращает кэшбэк по категориям за месяц."""
    result: dict[str, float] = {}

    for t in transactions:
        if "Дата операции" not in t or "Категория" not in t:
            continue

        date_str = t["Дата операции"]
        try:
            if " " in date_str:
                date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
            else:
                date = datetime.strptime(date_str, "%d.%m.%Y")
        except (ValueError, TypeError):
            continue

        if date.year != year or date.month != month:
            continue

        category = t["Категория"]
        cashback = t.get("Кэшбэк")

        if cashback is not None:
            result[category] = result.get(category, 0) + float(cashback)

    return {k: float(v) for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)}


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Рассчитывает инвестиции по округлению."""
    try:
        dt = datetime.strptime(month, "%Y-%m")
    except ValueError:
        return 0.0

    total_investment = 0.0

    for t in transactions:
        if "Дата операции" not in t:
            continue

        date_str = t["Дата операции"]
        try:
            date = datetime.strptime(date_str, "%d.%m.%Y")
        except (ValueError, TypeError):
            continue

        if date.year != dt.year or date.month != dt.month:
            continue

        amount = t.get("Сумма операции", 0)
        rounded = t.get("Сумма операции с округлением", 0)

        if amount < 0:
            diff = rounded - abs(amount)
            if diff <= limit:
                total_investment += diff

    return round(total_investment, 2)


def simple_search(query: str, transactions: list[dict[str, Any]]) -> str:
    """Простой поиск по транзакциям. Возвращает JSON строку."""
    if not query:
        return json.dumps([], ensure_ascii=False)

    query_lower = query.lower()
    results = []

    for t in transactions:
        description = str(t.get("Описание", "")).lower()
        category = str(t.get("Категория", "")).lower()

        if query_lower in description or query_lower in category:
            results.append(t)

    return json.dumps(results, ensure_ascii=False)


def find_phone_transactions(transactions: list[dict[str, Any]]) -> str:
    """Находит транзакции с номерами телефонов. Возвращает JSON строку."""
    phone_pattern = re.compile(r"[+]?[78][\s\-()]?\d{3}[\s\-()]?\d{3}[\s\-()]?\d{2}[\s\-()]?\d{2}")
    results = []

    for t in transactions:
        description = str(t.get("Описание", ""))
        if phone_pattern.search(description):
            results.append(t)

    return json.dumps(results, ensure_ascii=False)


def find_person_transfers(transactions: list[dict[str, Any]], name: Optional[str] = None) -> str:
    """Находит переводы физлицам. Возвращает JSON строку."""
    results = []

    for t in transactions:
        description = str(t.get("Описание", "")).lower()
        category = str(t.get("Категория", "")).lower()

        # Проверяем категорию "Переводы"
        is_transfer_category = "перевод" in category

        # Проверяем ключевые слова в описании
        transfer_keywords = ["перевод", "sbp", "сбп", "физлиц", "физ.лиц"]
        has_keyword = any(kw in description for kw in transfer_keywords)

        matches_name = name is None or name.lower() in description

        if (is_transfer_category or has_keyword) and matches_name:
            results.append(t)

    return json.dumps(results, ensure_ascii=False)
