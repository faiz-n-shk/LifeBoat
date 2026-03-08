"""
Activity Formatter
Formats activity log messages to be user-friendly and readable
"""
from datetime import datetime
from src.core.config import config


def format_currency(amount: float) -> str:
    """
    Format amount with currency symbol respecting prefix/suffix settings
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted currency string (e.g., "$50.00" or "50.00₹")
    """
    try:
        symbol = config.get('currency.symbol', '$')
        position = config.get('currency.position', 'prefix')
        decimal_places = config.get('currency.decimal_places', 2)
        
        # Format the amount
        formatted_amount = f"{abs(amount):.{decimal_places}f}"
        
        # Add symbol based on position
        if position == 'prefix':
            result = f"{symbol}{formatted_amount}"
        else:  # suffix
            result = f"{formatted_amount}{symbol}"
        
        # Add negative sign if needed
        if amount < 0:
            result = f"-{result}"
        
        return result
    except Exception:
        # Fallback to simple format
        return f"${amount:.2f}"


def format_expense_log(action: str, category: str, amount: float, description: str = None) -> tuple:
    """
    Format expense activity log message
    
    Args:
        action: Action type (created, updated, deleted)
        category: Expense category
        amount: Amount value
        description: Optional description
        
    Returns:
        Tuple of (action, details) for logging
    """
    formatted_amount = format_currency(amount)
    
    action_map = {
        'created': 'Added expense',
        'updated': 'Updated expense',
        'deleted': 'Deleted expense'
    }
    
    friendly_action = action_map.get(action, action)
    
    if description:
        details = f"{formatted_amount} for {category} - {description}"
    else:
        details = f"{formatted_amount} for {category}"
    
    return friendly_action, details


def format_income_log(action: str, source: str, amount: float, description: str = None) -> tuple:
    """
    Format income activity log message
    
    Args:
        action: Action type (created, updated, deleted)
        source: Income source
        amount: Amount value
        description: Optional description
        
    Returns:
        Tuple of (action, details) for logging
    """
    formatted_amount = format_currency(amount)
    
    action_map = {
        'created': 'Added income',
        'updated': 'Updated income',
        'deleted': 'Deleted income'
    }
    
    friendly_action = action_map.get(action, action)
    
    if description:
        details = f"{formatted_amount} from {source} - {description}"
    else:
        details = f"{formatted_amount} from {source}"
    
    return friendly_action, details


def format_event_log(action: str, title: str, date: datetime = None) -> tuple:
    """
    Format calendar event log message
    
    Args:
        action: Action type (created, updated, deleted)
        title: Event title
        date: Optional event date
        
    Returns:
        Tuple of (action, details) for logging
    """
    action_map = {
        'created': 'Created event',
        'updated': 'Updated event',
        'deleted': 'Deleted event'
    }
    
    friendly_action = action_map.get(action, action)
    
    if date:
        date_str = date.strftime('%d %b %Y')
        details = f'"{title}" on {date_str}'
    else:
        details = f'"{title}"'
    
    return friendly_action, details


def format_note_log(action: str, title: str, tags: list = None) -> tuple:
    """
    Format note log message
    
    Args:
        action: Action type (created, updated, deleted, pinned, unpinned)
        title: Note title
        tags: Optional list of tags
        
    Returns:
        Tuple of (action, details) for logging
    """
    action_map = {
        'created': 'Created note',
        'updated': 'Updated note',
        'deleted': 'Deleted note',
        'pinned': 'Pinned note',
        'unpinned': 'Unpinned note'
    }
    
    friendly_action = action_map.get(action, action)
    
    if tags and len(tags) > 0:
        tags_str = ', '.join(tags)
        details = f'"{title}" ({tags_str})'
    else:
        details = f'"{title}"'
    
    return friendly_action, details


def format_habit_log(action: str, name: str, habit_type: str = None) -> tuple:
    """
    Format habit log message
    
    Args:
        action: Action type (created, updated, deleted, completed, skipped)
        name: Habit name
        habit_type: Optional habit type (Good/Bad)
        
    Returns:
        Tuple of (action, details) for logging
    """
    action_map = {
        'created': 'Created habit',
        'updated': 'Updated habit',
        'deleted': 'Deleted habit',
        'completed': 'Completed habit',
        'incremented': 'Completed habit',
        'decremented': 'Uncompleted habit',
        'skipped': 'Skipped habit'
    }
    
    friendly_action = action_map.get(action.lower(), action)
    
    if habit_type:
        details = f'"{name}" ({habit_type})'
    else:
        details = f'"{name}"'
    
    return friendly_action, details


def format_settings_log(section: str, changes: list) -> tuple:
    """
    Format settings log message
    
    Args:
        section: Settings section (appearance, behavior, etc.)
        changes: List of changes made
        
    Returns:
        Tuple of (action, details) for logging
    """
    section_map = {
        'appearance': 'Appearance',
        'behavior': 'Behavior',
        'locale': 'Date & Currency',
        'advanced': 'Advanced',
        'themes': 'Theme',
        'paths': 'File Locations'
    }
    
    friendly_section = section_map.get(section.lower(), section)
    action = f'Changed {friendly_section} settings'
    
    if isinstance(changes, list) and len(changes) > 0:
        details = ', '.join(changes)
    else:
        details = str(changes)
    
    return action, details


def format_theme_log(action: str, theme_name: str, old_name: str = None) -> tuple:
    """
    Format theme log message
    
    Args:
        action: Action type (changed, created, edited, deleted, etc.)
        theme_name: Theme name
        old_name: Optional old theme name (for changes)
        
    Returns:
        Tuple of (action, details) for logging
    """
    action_map = {
        'changed': 'Switched theme',
        'created': 'Created theme',
        'edited': 'Edited theme',
        'deleted': 'Deleted theme',
        'customized': 'Customized theme',
        'renamed': 'Renamed theme'
    }
    
    friendly_action = action_map.get(action.lower(), action)
    
    if old_name:
        details = f'from "{old_name}" to "{theme_name}"'
    else:
        details = f'"{theme_name}"'
    
    return friendly_action, details
