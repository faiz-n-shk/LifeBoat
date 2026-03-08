"""
Default Configuration Template
Used to create config.yaml if it doesn't exist
"""

DEFAULT_CONFIG_YAML = """# Lifeboat v2 Configuration
# This file is auto-generated. Modify values as needed.

# Window Settings
window:
  width: 1280
  height: 720
  remember_size: true
  remember_position: true
  resolution: "custom"  # custom or preset like "1920x1080"
  monitor: 0  # Monitor index for multi-monitor setups

# Appearance
appearance:
  theme: "Dark"
  font_family: "Segoe UI"
  font_size: 10
  animation_duration: 200  # milliseconds
  enable_animations: true

# Date/Time Formats
datetime:
  date_format: "%d-%m-%Y"
  time_format: "%I:%M %p"
  datetime_format: "%d-%m-%Y %I:%M %p"
  display_date_format: "%d %B %Y"
  display_datetime_format: "%d %B %Y %I:%M %p"
  time_mode: "12hr"  # 12hr or 24hr
  week_start: "Monday"

# Currency Settings
currency:
  symbol: "₹"
  code: "INR"
  position: "prefix"  # prefix or suffix
  decimal_places: 2

# Categories
categories:
  expenses:
    - "Food & Dining"
    - "Transportation"
    - "Shopping"
    - "Entertainment"
    - "Bills & Utilities"
    - "Healthcare"
    - "Education"
    - "Travel"
    - "Personal Care"
    - "Groceries"
    - "Rent/Mortgage"
    - "Insurance"
    - "Investments"
    - "Gifts & Donations"
    - "Other"
  
  income:
    - "Salary"
    - "Freelance"
    - "Business"
    - "Investments"
    - "Gifts"
    - "Refunds"
    - "Other"

# Task Settings
tasks:
  priorities:
    - "Low"
    - "Medium"
    - "High"
    - "Urgent"
  
  statuses:
    - "Not Started"
    - "In Progress"
    - "Completed"
    - "On Hold"
    - "Cancelled"

# Calendar Settings
calendar:
  views:
    - "Month"
    - "Week"
    - "Day"
    - "Agenda"
  default_view: "Month"

# Dashboard Settings
dashboard:
  show_summary: true
  show_recent_items: true
  recent_items_count: 5

# Notes Settings
notes:
  view_mode: "Grid"  # Auto, Grid, List, or Compact
  tag_filter: "All Tags"
  pinned_filter: false

# Advanced Settings
advanced:
  show_debug_buttons: false  # Show reload/restart buttons in navigation
  auto_update_database: true  # Auto-update database on app updates
  recent_activity_mode: "all"  # Options: "session", "today", "3days", "standard" (7 days), "30days", "all", "none"
  log_rotation_hours: 168  # Hours before creating new log file (0=every startup, 24=1day, 48=2days, 72=3days, 168=1week, or custom)

# Behavior Settings
behavior:
  start_on_startup: false  # Start app when Windows starts
  start_minimized: false  # Start app minimized to tray
  minimize_to_tray: false  # Minimize to system tray instead of taskbar
  close_to_tray: false  # Close button minimizes to tray instead of quitting

"""


def create_default_config(config_path):
    """
    Create default config.yaml file
    
    Args:
        config_path: Path object where config should be created
    
    Returns:
        bool: True if created successfully
    """
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG_YAML)
        print(f"Created default config at: {config_path}")
        return True
    except Exception as e:
        print(f"Error creating default config: {e}")
        return False
