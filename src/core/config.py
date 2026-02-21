"""
Lifeboat - Configuration Module
Loads configuration from config.yaml
"""
import yaml
from pathlib import Path

# ============================================================================
# PATHS - Using Path Manager for custom locations
# ============================================================================

BASE_DIR = Path(__file__).parent.parent.parent

# Import path manager to get custom paths
try:
    from src.core.path_manager import path_manager
    CONFIG_FILE = path_manager.get_config_path()
    DATABASE_PATH = path_manager.get_database_path()
except ImportError:
    # Fallback if path_manager not available yet (first import)
    CONFIG_FILE = BASE_DIR / "config.yaml"
    DATABASE_PATH = BASE_DIR / "data" / "lifeboat.db"

ASSETS_DIR = BASE_DIR / "assets"
THEMES_DIR = BASE_DIR / "themes"  # Not used - themes stored in database
ICONS_DIR = ASSETS_DIR / "icons"
DATA_DIR = BASE_DIR / "data"

# Create required directories
for directory in [ASSETS_DIR, ICONS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

def load_config():
    """
    Load configuration from config.yaml
    Returns empty dict if file not found or invalid
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                print(f"Warning: {CONFIG_FILE} is empty. Using defaults.")
                return {}
            return config
    except FileNotFoundError:
        print(f"Warning: {CONFIG_FILE} not found. Using defaults.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}. Using defaults.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}. Using defaults.")
        return {}

# Load configuration
_config = load_config()

# ============================================================================
# APPLICATION INFORMATION
# ============================================================================

APP_NAME = _config.get('app', {}).get('name', 'Lifeboat')
APP_VERSION = _config.get('app', {}).get('version', '1.1.0')
APP_AUTHOR = _config.get('app', {}).get('author', 'Lifeboat Team')

# ============================================================================
# WINDOW SETTINGS
# ============================================================================

WINDOW_WIDTH = _config.get('window', {}).get('width', 1400)
WINDOW_HEIGHT = _config.get('window', {}).get('height', 900)
MIN_WINDOW_WIDTH = _config.get('window', {}).get('min_width', 1200)
MIN_WINDOW_HEIGHT = _config.get('window', {}).get('min_height', 700)

# ============================================================================
# UI SETTINGS
# ============================================================================

CORNER_RADIUS = _config.get('ui', {}).get('corner_radius', 6)
BORDER_WIDTH = _config.get('ui', {}).get('border_width', 1)

# ============================================================================
# FONT SETTINGS
# ============================================================================

FONT_FAMILY = _config.get('fonts', {}).get('family', 'Segoe UI')
_font_sizes = _config.get('fonts', {}).get('size', {})
FONT_SIZE_SMALL = _font_sizes.get('small', 11)
FONT_SIZE_NORMAL = _font_sizes.get('normal', 13)
FONT_SIZE_LARGE = _font_sizes.get('large', 16)
FONT_SIZE_XLARGE = _font_sizes.get('xlarge', 20)

# ============================================================================
# DATE/TIME FORMATS
# ============================================================================

_datetime = _config.get('datetime', {})
DATE_FORMAT = _datetime.get('date_format', '%d-%m-%Y')
TIME_FORMAT = _datetime.get('time_format', '%I:%M %p')
DATETIME_FORMAT = _datetime.get('datetime_format', '%d-%m-%Y %I:%M %p')
DISPLAY_DATE_FORMAT = _datetime.get('display_date_format', '%d %B %Y')
DISPLAY_DATETIME_FORMAT = _datetime.get('display_datetime_format', '%d %B %Y %I:%M %p')
TIME_MODE = _datetime.get('time_mode', '12hr')

# ============================================================================
# CURRENCY SETTINGS
# ============================================================================

_currency = _config.get('currency', {})
CURRENCY_SYMBOL = _currency.get('symbol', '₹')
CURRENCY_CODE = _currency.get('code', 'INR')
CURRENCY_POSITION = _currency.get('position', 'prefix')
CURRENCY_DECIMAL_PLACES = _currency.get('decimal_places', 2)

# ============================================================================
# DEFAULT THEMES
# ============================================================================

# Fallback theme if config.yaml is missing or invalid
_DEFAULT_DARK_THEME = {
    "Dark": {
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2d2d2d",
        "bg_tertiary": "#3d3d3d",
        "fg_primary": "#ffffff",
        "fg_secondary": "#b0b0b0",
        "accent": "#0078d4",
        "accent_hover": "#106ebe",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "border": "#4d4d4d"
    }
}

DEFAULT_THEMES = _config.get('themes', _DEFAULT_DARK_THEME)

# ============================================================================
# CATEGORIES
# ============================================================================

_categories = _config.get('categories', {})
EXPENSE_CATEGORIES = _categories.get('expenses', [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Bills & Utilities", "Healthcare", "Education", "Travel",
    "Personal Care", "Groceries", "Rent/Mortgage", "Insurance",
    "Investments", "Gifts & Donations", "Other"
])
INCOME_CATEGORIES = _categories.get('income', [
    "Salary", "Freelance", "Business", "Investments",
    "Gifts", "Refunds", "Other"
])

# ============================================================================
# TASK SETTINGS
# ============================================================================

_tasks = _config.get('tasks', {})
TASK_PRIORITIES = _tasks.get('priorities', ["Low", "Medium", "High", "Urgent"])
TASK_STATUSES = _tasks.get('statuses', [
    "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"
])

# ============================================================================
# CALENDAR SETTINGS
# ============================================================================

_calendar = _config.get('calendar', {})
CALENDAR_VIEWS = _calendar.get('views', ["Month", "Week", "Day", "Agenda"])

# ============================================================================
# CLEANUP
# ============================================================================

# Remove private variables from module namespace
del _config, _font_sizes, _datetime, _currency, _categories, _tasks, _calendar, _DEFAULT_DARK_THEME
