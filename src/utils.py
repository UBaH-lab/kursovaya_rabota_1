"""Модуль с вспомогательными функциями."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.

    Args:
        filepath: Путь к файлу с транзакциями.

    Returns:
        DataFrame с транзакциями.
    """
    # TODO: Реализовать загрузку
    pass


def load_user_settings(filepath: str = "user_settings.json") -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON-файла.

    Args:
        filepath: Путь к файлу с настройками.

    Returns:
        Словарь с настройками.
    """
    pass


def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """
    Получает курсы валют через API.

    Args:
        currencies: Список кодов валют.

    Returns:
        Список курсов валют.
    """
    pass


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """
    Получает цены акций через API.

    Args:
        stocks: Список тикеров акций.

    Returns:
        Список цен акций.
    """
    pass