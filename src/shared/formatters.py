"""
Data Formatters
Utilities for formatting data according to user preferences
"""
from datetime import datetime, time
from typing import Union

from src.core.config import config


# Currency mapping: symbol -> code
CURRENCY_MAP = {
    "₹": "INR",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₽": "RUB",
    "₩": "KRW",
    "₪": "ILS",
    "₦": "NGN",
    "R": "ZAR",
    "R$": "BRL",
    "C$": "CAD",
    "A$": "AUD",
    "CHF": "CHF",
    "kr": "SEK",
}


def get_currency_code(symbol: str) -> str:
    """Get currency code from symbol"""
    return CURRENCY_MAP.get(symbol, "USD")


def get_available_currencies() -> list:
    """Get list of available currencies"""
    return list(CURRENCY_MAP.keys())


def format_currency(amount: Union[float, int]) -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Amount to format
    
    Returns:
        Formatted currency string
    """
    symbol = config.get('currency.symbol', '₹')
    position = config.get('currency.position', 'prefix')
    decimal_places = config.get('currency.decimal_places', 2)
    
    # Format amount
    formatted_amount = f"{float(amount):.{decimal_places}f}"
    
    # Apply position
    if position == 'suffix':
        return f"{formatted_amount} {symbol}"
    else:  # prefix
        return f"{symbol} {formatted_amount}"


def format_time(time_obj: Union[datetime, time]) -> str:
    """
    Format time according to user preference
    
    Args:
        time_obj: Time or datetime object
    
    Returns:
        Formatted time string
    """
    time_mode = config.get('datetime.time_mode', '12hr')
    
    if isinstance(time_obj, datetime):
        time_obj = time_obj.time()
    
    if time_mode == '24hr':
        return time_obj.strftime('%H:%M')
    else:  # 12hr
        return time_obj.strftime('%I:%M %p')


def format_date(date_obj: datetime) -> str:
    """
    Format date according to user preference
    
    Args:
        date_obj: Date or datetime object
    
    Returns:
        Formatted date string
    """
    date_format = config.get('datetime.date_format', '%d-%m-%Y')
    return date_obj.strftime(date_format)


def format_datetime(datetime_obj: datetime) -> str:
    """
    Format datetime according to user preference
    
    Args:
        datetime_obj: Datetime object
    
    Returns:
        Formatted datetime string
    """
    date_str = format_date(datetime_obj)
    time_str = format_time(datetime_obj)
    return f"{date_str} {time_str}"
