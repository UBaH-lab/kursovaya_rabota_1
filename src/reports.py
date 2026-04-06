"""Модуль для формирования отчётов."""

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def _get_date_range(date: Optional[str] = None) -> Tuple[datetime, datetime]:
    """Возвращает диапазон дат за 90 дней."""
    if date:
        try:
            end = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            end = datetime.now()
    else:
        end = datetime.now()
    start = end - timedelta(days=90)
    return start, end


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по категории за 90 дней."""
    start, end = _get_date_range(date)

    if "Дата операции" not in transactions.columns or "Категория" not in transactions.columns:
        return pd.DataFrame()

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    mask = (df["Категория"] == category) & (df["Дата операции"] >= start) & (df["Дата операции"] <= end)
    return df[mask].reset_index(drop=True)


def spending_by_weekday(transactions: pd.DataFrame) -> pd.DataFrame:
    """Возвращает средние траты по дням недели."""
    if len(transactions) == 0 or "Дата операции" not in transactions.columns:
        return pd.DataFrame()

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    df["День недели"] = df["Дата операции"].dt.day_name()

    if "Сумма" not in df.columns:
        return pd.DataFrame()

    result = df.groupby("День недели")["Сумма"].mean().reset_index()
    result.columns = ["День недели", "Средняя сумма"]
    return result


def spending_by_workday(transactions: pd.DataFrame) -> pd.DataFrame:
    """Возвращает средние траты по типу дня."""
    if len(transactions) == 0 or "Дата операции" not in transactions.columns:
        return pd.DataFrame()

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    df["Тип дня"] = df["Дата операции"].dt.dayofweek.apply(lambda x: "Выходной" if x >= 5 else "Рабочий")

    if "Сумма" not in df.columns:
        return pd.DataFrame()

    result = df.groupby("Тип дня")["Сумма"].mean().reset_index()
    result.columns = ["Тип дня", "Средняя сумма"]
    return result


def save_report(filename: Optional[str] = None):
    """Декоратор для сохранения отчёта в файл."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            if filename:
                try:
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "w", encoding="utf-8") as f:
                        if isinstance(result, pd.DataFrame):
                            json.dump(result.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
                        else:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                    logger.info(f"Отчёт сохранён: {filename}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения: {e}")
            return result

        return wrapper

    return decorator
