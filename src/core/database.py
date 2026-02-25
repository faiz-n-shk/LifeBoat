"""
Database Management
SQLite database with Peewee ORM
"""
from peewee import *
from datetime import datetime
from pathlib import Path

from src.core.config import DATA_DIR

# Database path
DATABASE_PATH = DATA_DIR / "lifeboat.db"

# Initialize database
db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    """Base model for all database models"""
    class Meta:
        database = db


def initialize_database():
    """Initialize database and create tables"""
    import os
    import shutil
    from src.models import (
        Event, Task, Expense, Income, Goal, 
        Habit, HabitLog, Note, Theme, Settings
    )
    
    db_exists = os.path.exists(DATABASE_PATH)
    
    db.connect()
    
    # Enable SQLite optimizations
    db.execute_sql('PRAGMA journal_mode=WAL')
    db.execute_sql('PRAGMA synchronous=NORMAL')
    db.execute_sql('PRAGMA cache_size=10000')
    db.execute_sql('PRAGMA temp_store=MEMORY')
    
    if not db_exists:
        print("Creating fresh database...")
        
        # Create all tables
        db.create_tables([
            Event, Task, Expense, Income, Goal,
            Habit, HabitLog, Note, Theme, Settings
        ])
        
        # Create default themes
        default_themes = get_default_themes()
        with db.atomic():
            for theme_name, theme_colors in default_themes.items():
                Theme.create(
                    name=theme_name,
                    is_active=theme_name == "Dark",
                    is_custom=False,
                    **theme_colors
                )
            
            # Create default settings
            Settings.create(key='first_run', value='true')
            Settings.create(key='currency_symbol', value='₹')
            Settings.create(key='week_start', value='Monday')
        
        print("Database created with default data")
        
        # Close connection before copying
        db.close()
        
        # Create template for restore
        try:
            template_path = DATABASE_PATH.parent / "default_settings.db"
            shutil.copy2(DATABASE_PATH, template_path)
            print(f"Created database template at: {template_path}")
        except Exception as e:
            print(f"Warning: Could not create database template: {e}")
        
        db.connect()
    else:
        # Ensure tables exist (safe mode)
        db.create_tables([
            Event, Task, Expense, Income, Goal,
            Habit, HabitLog, Note, Theme, Settings
        ], safe=True)
    
    db.close()
    print("Database initialized")


def get_default_themes():
    """Get default theme definitions"""
    return {
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
