"""
Lifeboat - Utility Functions
utils helper file
"""
from datetime import datetime, timedelta
import calendar
from typing import List, Tuple
from src.core import config

def format_date(date, format_string=None):
    """Format a date object to string"""
    if not date:
        return ""
    if format_string is None:
        format_string = config.DISPLAY_DATE_FORMAT
    if isinstance(date, str):
        date = datetime.strptime(date, config.DATE_FORMAT)
    return date.strftime(format_string)

def format_datetime(dt, format_string=None):
    """Format a datetime object to string"""
    if not dt:
        return ""
    if format_string is None:
        format_string = config.DISPLAY_DATETIME_FORMAT
    if isinstance(dt, str):
        dt = datetime.strptime(dt, config.DATETIME_FORMAT)
    return dt.strftime(format_string)

def parse_date(date_string, format_string=None):
    """Parse a date string to datetime object"""
    if not date_string:
        return None
    if format_string is None:
        format_string = config.DATE_FORMAT
    try:
        return datetime.strptime(date_string, format_string)
    except:
        return None

def get_month_calendar(year, month):
    """Get calendar data for a specific month"""
    cal = calendar.monthcalendar(year, month)
    return cal

def get_week_dates(date):
    """Get all dates in the week containing the given date"""
    start = date - timedelta(days=date.weekday())
    return [start + timedelta(days=i) for i in range(7)]

def get_date_range(start_date, end_date):
    """Get list of dates between start and end"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def format_currency(amount, symbol='$'):
    """Format amount as currency"""
    return f"{symbol}{amount:,.2f}"

def calculate_percentage(part, whole):
    """Calculate percentage"""
    if whole == 0:
        return 0
    return (part / whole) * 100

def truncate_text(text, max_length=50):
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_color_brightness(hex_color):
    """Calculate brightness of a hex color (0-255)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r * 299 + g * 587 + b * 114) / 1000

def is_dark_color(hex_color):
    """Check if a color is dark"""
    return get_color_brightness(hex_color) < 128

def get_contrasting_text_color(bg_color):
    """Get contrasting text color (black or white) for a background"""
    return "#000000" if not is_dark_color(bg_color) else "#ffffff"

def get_week_number(date):
    """Get ISO week number"""
    return date.isocalendar()[1]

def get_days_until(target_date):
    """Get number of days until target date"""
    if isinstance(target_date, str):
        target_date = parse_date(target_date)
    today = datetime.now().date()
    if hasattr(target_date, 'date'):
        target_date = target_date.date()
    delta = target_date - today
    return delta.days

def get_month_name(month_number):
    """Get month name from number"""
    return calendar.month_name[month_number]

def get_weekday_name(weekday_number):
    """Get weekday name from number (0=Monday)"""
    return calendar.day_name[weekday_number]

def sort_by_priority(items, priority_field='priority'):
    """Sort items by priority"""
    from src.core.config import TASK_PRIORITIES
    priority_order = {p: i for i, p in enumerate(TASK_PRIORITIES)}
    return sorted(items, key=lambda x: priority_order.get(getattr(x, priority_field), 999))

def filter_by_date_range(items, start_date, end_date, date_field='date'):
    """Filter items by date range"""
    filtered = []
    for item in items:
        item_date = getattr(item, date_field)
        if hasattr(item_date, 'date'):
            item_date = item_date.date()
        if start_date <= item_date <= end_date:
            filtered.append(item)
    return filtered

def generate_color_palette(base_color, count=5):
    """Generate a color palette from a base color"""
    hex_color = base_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    palette = []
    for i in range(count):
        factor = 0.5 + (i * 0.5 / count)
        new_r = min(255, int(r * factor))
        new_g = min(255, int(g * factor))
        new_b = min(255, int(b * factor))
        palette.append(f"#{new_r:02x}{new_g:02x}{new_b:02x}")
    
    return palette
