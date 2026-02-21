"""
Lifeboat - Default Configuration Template
Used to create config.yaml if it doesn't exist
"""

DEFAULT_CONFIG_YAML = """# Lifeboat Configuration File
# This file is auto-generated. Modify values as needed.
# DO NOT change app name, version, or author - these are managed internally.

# Window Settings
window:
  width: 1280
  height: 720
  min_width: 1024
  min_height: 768

# UI Settings
ui:
  corner_radius: 6
  border_width: 1

# Font Settings
fonts:
  family: "Segoe UI"
  size:
    small: 11
    normal: 13
    large: 16
    xlarge: 20

# Date/Time Formats
datetime:
  date_format: "%d-%m-%Y"
  time_format: "%I:%M %p"
  datetime_format: "%d-%m-%Y %I:%M %p"
  display_date_format: "%d %B %Y"
  display_datetime_format: "%d %B %Y %I:%M %p"
  time_mode: "12hr"  # 12hr or 24hr

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

# Theme settings are managed through the UI
# Custom themes are stored in the database
"""

def create_default_config(config_path):
    """
    Create default config.yaml file
    
    Args:
        config_path: Path object where config should be created
    
    Returns:
        bool: True if created successfully, False otherwise
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
