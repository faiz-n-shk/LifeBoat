"""
Lifeboat - Configuration Module
Handles app-wide configuration and constants
"""
import os
from pathlib import Path

# App Information
APP_NAME = "Lifeboat"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Lifeboat Team"

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATABASE_PATH = BASE_DIR / "data" / "lifeboat.db"
ASSETS_DIR = BASE_DIR / "assets"
THEMES_DIR = BASE_DIR / "themes"
ICONS_DIR = ASSETS_DIR / "icons"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
for directory in [ASSETS_DIR, THEMES_DIR, ICONS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Default Theme Definitions
DEFAULT_THEMES = {
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
    }
}

# Window Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

# Font Settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 13
FONT_SIZE_LARGE = 16
FONT_SIZE_XLARGE = 20

# Date/Time Formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_DATE_FORMAT = "%B %d, %Y"
DISPLAY_DATETIME_FORMAT = "%B %d, %Y %I:%M %p"

# Expense Categories
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Personal Care",
    "Groceries",
    "Rent/Mortgage",
    "Insurance",
    "Investments",
    "Gifts & Donations",
    "Other"
]

# Income Categories
INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Business",
    "Investments",
    "Gifts",
    "Refunds",
    "Other"
]

# Task Priority Levels
TASK_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

# Task Status Options
TASK_STATUSES = ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"]

# Calendar View Options
CALENDAR_VIEWS = ["Month", "Week", "Day", "Agenda"]
