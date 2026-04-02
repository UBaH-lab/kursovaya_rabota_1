"""Модуль с функциями для формирования отчетов."""

import json
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения отчета в файл.

    Args:
        filename: Имя файла для сохранения (опционально).

    Returns:
        Декоратор.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            # TODO: Реализовать сохранение в файл
            return result

        return wrapper

    return decorator


def spending_by_category(
        transactions: pd.DataFrame,
        category: str,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями.
        category: Название категории.
        date: Дата отсчета (опционально).

    Returns:
        DataFrame с отфильтрованными транзакциями.
    """
    pass


def spending_by_weekday(
        transactions: pd.DataFrame,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает средние траты по дням недели за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями.
        date: Дата отсчета (опционально).

    Returns:
        DataFrame со средними тратами по дням недели.
    """
    pass


def spending_by_workday(
        transactions: pd.DataFrame,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает средние траты в рабочий и выходной день.

    Args:
        transactions: DataFrame с транзакциями.
        date: Дата отсчета (опционально).

    Returns:
        DataFrame со средними тратами.
    """
    pass