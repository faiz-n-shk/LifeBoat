"""
Lifeboat - Configuration Module
Loads configuration from config.yaml with hot-reload support
"""
import yaml
from pathlib import Path

# Import application constants (read-only metadata)
from src.core.constants import APP_NAME, APP_VERSION, APP_AUTHOR

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

def ensure_config_exists():
    """
    Ensure config.yaml exists, create from template if missing
    """
    if not CONFIG_FILE.exists():
        print(f"config.yaml not found. Creating default at: {CONFIG_FILE}")
        try:
            from src.core.config_template import create_default_config
            create_default_config(CONFIG_FILE)
        except Exception as e:
            print(f"Error creating default config: {e}")

def load_config():
    """
    Load configuration from config.yaml
    Creates default config if not found
    Returns empty dict if invalid
    """
    # Ensure config exists before loading
    ensure_config_exists()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                print(f"Warning: {CONFIG_FILE} is empty. Using defaults.")
                return {}
            return config
    except FileNotFoundError:
        print(f"Warning: {CONFIG_FILE} not found after creation attempt. Using defaults.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}. Using defaults.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}. Using defaults.")
        return {}

def reload_config():
    """
    Reload configuration from file
    Updates all module-level variables (except APP_NAME, APP_VERSION, APP_AUTHOR)
    """
    global _config
    global WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
    global CORNER_RADIUS, BORDER_WIDTH
    global FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, FONT_SIZE_XLARGE
    global DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT, DISPLAY_DATE_FORMAT, DISPLAY_DATETIME_FORMAT, TIME_MODE
    global CURRENCY_SYMBOL, CURRENCY_CODE, CURRENCY_POSITION, CURRENCY_DECIMAL_PLACES
    global DEFAULT_THEMES, EXPENSE_CATEGORIES, INCOME_CATEGORIES
    global TASK_PRIORITIES, TASK_STATUSES, CALENDAR_VIEWS
    
    _config = load_config()
    
    # Window Settings
    WINDOW_WIDTH = _config.get('window', {}).get('width', 1400)
    WINDOW_HEIGHT = _config.get('window', {}).get('height', 900)
    MIN_WINDOW_WIDTH = _config.get('window', {}).get('min_width', 1200)
    MIN_WINDOW_HEIGHT = _config.get('window', {}).get('min_height', 700)
    
    # UI Settings
    CORNER_RADIUS = _config.get('ui', {}).get('corner_radius', 6)
    BORDER_WIDTH = _config.get('ui', {}).get('border_width', 1)
    
    # Font Settings
    FONT_FAMILY = _config.get('fonts', {}).get('family', 'Segoe UI')
    _font_sizes = _config.get('fonts', {}).get('size', {})
    FONT_SIZE_SMALL = _font_sizes.get('small', 11)
    FONT_SIZE_NORMAL = _font_sizes.get('normal', 13)
    FONT_SIZE_LARGE = _font_sizes.get('large', 16)
    FONT_SIZE_XLARGE = _font_sizes.get('xlarge', 20)
    
    # Date/Time Formats
    _datetime = _config.get('datetime', {})
    DATE_FORMAT = _datetime.get('date_format', '%d-%m-%Y')
    TIME_FORMAT = _datetime.get('time_format', '%I:%M %p')
    DATETIME_FORMAT = _datetime.get('datetime_format', '%d-%m-%Y %I:%M %p')
    DISPLAY_DATE_FORMAT = _datetime.get('display_date_format', '%d %B %Y')
    DISPLAY_DATETIME_FORMAT = _datetime.get('display_datetime_format', '%d %B %Y %I:%M %p')
    TIME_MODE = _datetime.get('time_mode', '12hr')
    
    # Currency Settings
    _currency = _config.get('currency', {})
    CURRENCY_SYMBOL = _currency.get('symbol', '₹')
    CURRENCY_CODE = _currency.get('code', 'INR')
    CURRENCY_POSITION = _currency.get('position', 'prefix')
    CURRENCY_DECIMAL_PLACES = _currency.get('decimal_places', 2)
    
    # Default Themes (use module-level _DEFAULT_THEMES)
    DEFAULT_THEMES = _config.get('themes', _DEFAULT_THEMES)
    
    # Categories
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
    
    # Task Settings
    _tasks = _config.get('tasks', {})
    TASK_PRIORITIES = _tasks.get('priorities', ["Low", "Medium", "High", "Urgent"])
    TASK_STATUSES = _tasks.get('statuses', [
        "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"
    ])
    
    # Calendar Settings
    _calendar = _config.get('calendar', {})
    CALENDAR_VIEWS = _calendar.get('views', ["Month", "Week", "Day", "Agenda"])

# Load configuration initially
_config = load_config()

# ============================================================================
# APPLICATION INFORMATION (Read-only from constants.py)
# ============================================================================

# APP_NAME, APP_VERSION, APP_AUTHOR are imported from constants.py
# Users cannot modify these values via config.yaml

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

# Fallback themes if config.yaml is missing or invalid
_DEFAULT_THEMES = {
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
    },
    "Light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f3f3f3",
        "bg_tertiary": "#e8e8e8",
        "fg_primary": "#000000",
        "fg_secondary": "#616161",
        "accent": "#005fb8",
        "accent_hover": "#004c99",
        "success": "#16825d",
        "warning": "#ca5010",
        "danger": "#d13438",
        "border": "#d4d4d4"
    },
    "Catppuccin Mocha": {
        "bg_primary": "#1e1e2e",
        "bg_secondary": "#313244",
        "bg_tertiary": "#45475a",
        "fg_primary": "#cdd6f4",
        "fg_secondary": "#bac2de",
        "accent": "#89b4fa",
        "accent_hover": "#74c7ec",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "danger": "#f38ba8",
        "border": "#585b70"
    },
    "Cyberpunk": {
        "bg_primary": "#0a0e27",
        "bg_secondary": "#16213e",
        "bg_tertiary": "#1a1a2e",
        "fg_primary": "#00ff41",
        "fg_secondary": "#00d9ff",
        "accent": "#ff00ff",
        "accent_hover": "#ff00aa",
        "success": "#00ff41",
        "warning": "#ffff00",
        "danger": "#ff0055",
        "border": "#00d9ff"
    },
    "Matrix": {
        "bg_primary": "#0d0208",
        "bg_secondary": "#1a1a1a",
        "bg_tertiary": "#0f3d0f",
        "fg_primary": "#00ff41",
        "fg_secondary": "#00cc33",
        "accent": "#00ff41",
        "accent_hover": "#00cc33",
        "success": "#00ff41",
        "warning": "#39ff14",
        "danger": "#ff0000",
        "border": "#003b00"
    }
}

DEFAULT_THEMES = _config.get('themes', _DEFAULT_THEMES)

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
