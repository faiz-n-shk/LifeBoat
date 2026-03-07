"""
Database Management
SQLite database with Peewee ORM
"""
import logging
from peewee import * #type: ignore
from datetime import datetime
from pathlib import Path
from src.core.debug import debug_log

logger = logging.getLogger(__name__)

# Get database path from path_manager
def get_database_path():
    """Get the correct database path (custom or default)"""
    from src.core.path_manager import path_manager
    db_path = path_manager.get_database_path()
    debug_log('Database.get_database_path', f"Resolved to: {db_path}")
    return db_path

# Initialize database with dynamic path
DATABASE_PATH = get_database_path()
db = SqliteDatabase(str(DATABASE_PATH))

debug_log('Database', f"Using database at: {DATABASE_PATH}")


class BaseModel(Model):
    """Base model for all database models"""
    class Meta:
        database = db


def initialize_database():
    """Initialize database and create tables"""
    import os
    from src.models import (
        Event, Expense, Income, 
        Habit, HabitLog, Note, Theme, Settings
    )
    
    db_exists = os.path.exists(DATABASE_PATH)
    logger.info(f"Initializing database at: {DATABASE_PATH} (exists: {db_exists})")
    
    try:
        db.connect()
        logger.info("Database connection established")
        
        # Enable SQLite optimizations
        db.execute_sql('PRAGMA journal_mode=WAL')
        db.execute_sql('PRAGMA synchronous=NORMAL')
        db.execute_sql('PRAGMA cache_size=10000')
        db.execute_sql('PRAGMA temp_store=MEMORY')
        logger.info("SQLite optimizations applied")
        
        if not db_exists:
            logger.info("Creating fresh database...")
            
            # Create all tables
            db.create_tables([
                Event, Expense, Income,
                Habit, HabitLog, Note, Theme, Settings
            ])
            logger.info("Database tables created")
            
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
                logger.info(f"Created {len(default_themes)} default themes")
                
                # Create default settings
                Settings.create(key='first_run', value='true')
                Settings.create(key='currency_symbol', value='₹')
                Settings.create(key='week_start', value='Monday')
                logger.info("Created default settings")
            
            logger.info("Database created with default data")
        else:
            # Ensure tables exist (safe mode)
            db.create_tables([
                Event, Expense, Income,
                Habit, HabitLog, Note, Theme, Settings
            ], safe=True)
            logger.info("Verified database tables exist")
        
        db.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise

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
            "bg_primary": "#faf8f3",
            "bg_secondary": "#f5f1e8",
            "bg_tertiary": "#ebe6dc",
            "fg_primary": "#2c2416",
            "fg_secondary": "#5c5445",
            "accent": "#d97706",
            "accent_hover": "#b45309",
            "success": "#059669",
            "warning": "#dc2626",
            "danger": "#dc2626",
            "border": "#d4cfc3"
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
