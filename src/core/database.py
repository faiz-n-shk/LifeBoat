"""
Database Management
SQLite database with Peewee ORM
"""
from peewee import *
from datetime import datetime
from pathlib import Path

# Get database path from path_manager
def get_database_path():
    """Get the correct database path (custom or default)"""
    from src.core.path_manager import path_manager
    db_path = path_manager.get_database_path()
    print(f"[Database.get_database_path] Resolved to: {db_path}")
    return db_path

# Initialize database with dynamic path
DATABASE_PATH = get_database_path()
db = SqliteDatabase(str(DATABASE_PATH))

print(f"[Database] Using database at: {DATABASE_PATH}")


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
        Habit, HabitLog, Note, Theme, Settings, Todo
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
            Habit, HabitLog, Note, Theme, Settings, Todo
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
            print(f"[Database] Created database template at: {template_path}")
        except Exception as e:
            print(f"[Database] Warning: Could not create database template: {e}")
        
        db.connect()
    else:
        # Ensure tables exist (safe mode)
        db.create_tables([
            Event, Task, Expense, Income, Goal,
            Habit, HabitLog, Note, Theme, Settings, Todo
        ], safe=True)
        
        # Run migrations for existing databases
        # run_migrations()
    
    db.close()
    print("Database initialized")

"""
def run_migrations():
    Run database migrations for schema updates
    try:
        # Migration 1: Add habit_type column to Habit table
        cursor = db.execute_sql("PRAGMA table_info(habit)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'habit_type' not in columns:
            print("Running migration: Adding habit_type column to Habit table...")
            db.execute_sql("ALTER TABLE habit ADD COLUMN habit_type VARCHAR(255) DEFAULT 'Good'")
            print("Migration completed: habit_type column added")
        
        # Migration 2: Add target_days column to Habit table
        if 'target_days' not in columns:
            print("Running migration: Adding target_days column to Habit table...")
            db.execute_sql("ALTER TABLE habit ADD COLUMN target_days INTEGER DEFAULT 7")
            print("Migration completed: target_days column added")
        
        # Migration 3: Add start_date column to Habit table
        if 'start_date' not in columns:
            print("Running migration: Adding start_date column to Habit table...")
            # Use current date as default for existing habits
            from datetime import date
            today = date.today().isoformat()
            db.execute_sql(f"ALTER TABLE habit ADD COLUMN start_date DATE DEFAULT '{today}'")
            print("Migration completed: start_date column added")
        
        # Migration 4: Set default values for frequency if it exists
        if 'frequency' in columns:
            print("Running migration: Setting default frequency values...")
            db.execute_sql("UPDATE habit SET frequency = 'Daily' WHERE frequency IS NULL")
            print("Migration completed: frequency defaults set")
        
        # Migration 5: Update Matrix theme colors for better visibility
        try:
            print("Running migration: Updating Matrix theme colors...")
            # Import Theme model inside migration
            from src.models.theme import Theme as ThemeModel
            matrix_theme = ThemeModel.get_or_none(ThemeModel.name == "Matrix")
            if matrix_theme:
                # Only update if colors haven't been updated yet
                if matrix_theme.bg_tertiary == "#0f3d0f":
                    matrix_theme.bg_tertiary = "#0a0a0a"
                    matrix_theme.fg_secondary = "#33ff66"
                    matrix_theme.save()
                    print("Migration completed: Matrix theme colors updated")
                else:
                    print("Matrix theme already updated, skipping...")
        except Exception as e:
            print(f"Matrix theme migration error: {e}")
        
        # Migration 6: Update Light theme for better appearance
        try:
            print("Running migration: Updating Light theme colors...")
            from src.models.theme import Theme as ThemeModel
            light_theme = ThemeModel.get_or_none(ThemeModel.name == "Light")
            if light_theme:
                # Only update if colors haven't been updated yet (check old bg_primary)
                if light_theme.bg_primary == "#ffffff":
                    light_theme.bg_primary = "#f5f5f5"
                    light_theme.bg_secondary = "#ffffff"
                    light_theme.bg_tertiary = "#e8e8e8"
                    light_theme.fg_primary = "#1e1e1e"
                    light_theme.fg_secondary = "#424242"
                    light_theme.accent = "#0078d4"
                    light_theme.accent_hover = "#106ebe"
                    light_theme.border = "#d0d0d0"
                    light_theme.save()
                    print("Migration completed: Light theme colors updated")
                else:
                    print("Light theme already updated, skipping...")
        except Exception as e:
            print(f"Light theme migration error: {e}")
    except Exception as e:
        print(f"Migration error: {e}")

"""
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
            "bg_primary": "#f5f5f5",
            "bg_secondary": "#ffffff",
            "bg_tertiary": "#e8e8e8",
            "fg_primary": "#1e1e1e",
            "fg_secondary": "#424242",
            "accent": "#0078d4",
            "accent_hover": "#106ebe",
            "success": "#16825d",
            "warning": "#ca5010",
            "danger": "#d13438",
            "border": "#d0d0d0"
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
            "bg_tertiary": "#0a0a0a",
            "fg_primary": "#00ff41",
            "fg_secondary": "#33ff66",
            "accent": "#00ff41",
            "accent_hover": "#00cc33",
            "success": "#00ff41",
            "warning": "#39ff14",
            "danger": "#ff0000",
            "border": "#003b00"
        }
    }
