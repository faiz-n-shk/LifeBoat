"""
Database Migration System
Handles database schema updates and migrations
"""
from peewee import *
from src.core.database import db, get_database_path
from src.core.config import config
from src.core.constants import APP_VERSION
import traceback


def get_database_version():
    """Get current database version from settings"""
    try:
        from src.models import Settings
        db.connect(reuse_if_open=True)
        version_setting = Settings.select().where(Settings.key == 'database_version').first()
        db.close()
        
        if version_setting:
            return version_setting.value
        return "0.0.0"  # No version means very old database
    except Exception as e:
        print(f"Error getting database version: {e}")
        return "0.0.0"


def set_database_version(version: str):
    """Set database version in settings"""
    try:
        from src.models import Settings
        db.connect(reuse_if_open=True)
        
        version_setting = Settings.select().where(Settings.key == 'database_version').first()
        if version_setting:
            version_setting.value = version
            version_setting.save()
        else:
            Settings.create(key='database_version', value=version)
        
        db.close()
        print(f"Database version set to: {version}")
        return True
    except Exception as e:
        print(f"Error setting database version: {e}")
        return False


def needs_migration():
    """Check if database needs migration"""
    db_version = get_database_version()
    app_version = APP_VERSION
    
    # If versions don't match, migration might be needed
    return db_version != app_version


def run_migrations(force: bool = False):
    """
    Run database migrations to update schema
    
    Args:
        force: Force migration even if versions match
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        db_version = get_database_version()
        app_version = APP_VERSION
        
        print(f"Database version: {db_version}")
        print(f"App version: {app_version}")
        
        if not force and db_version == app_version:
            return (True, "Database is already up to date!")
        
        # Import all models
        from src.models import (
            Event, Expense, Income,
            Habit, HabitLog, Note, Theme, Settings
        )
        
        db.connect(reuse_if_open=True)
        
        # List of all tables
        all_tables = [Event, Expense, Income, Habit, HabitLog, Note, Theme, Settings]
        
        migration_log = []
        
        # Step 1: Create any missing tables
        for table in all_tables:
            if not table.table_exists():
                db.create_tables([table])
                migration_log.append(f"Created table: {table._meta.table_name}")
        
        # Step 2: Add missing columns to existing tables
        for table in all_tables:
            if table.table_exists():
                # Get existing columns
                cursor = db.execute_sql(f"PRAGMA table_info({table._meta.table_name})")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Get model fields
                model_fields = {field.name for field in table._meta.fields.values()}
                
                # Find missing columns
                missing_columns = model_fields - existing_columns
                
                if missing_columns:
                    for col_name in missing_columns:
                        field = table._meta.fields[col_name]
                        
                        # Build ALTER TABLE statement
                        field_type = field.field_type
                        
                        # For NOT NULL columns without a default, make them nullable during migration
                        if not field.null and field.default is None:
                            null_clause = "NULL"  # Allow NULL during migration
                        else:
                            null_clause = "NULL" if field.null else "NOT NULL"
                        
                        default_clause = ""
                        
                        if field.default is not None:
                            if isinstance(field.default, str):
                                default_clause = f"DEFAULT '{field.default}'"
                            elif isinstance(field.default, bool):
                                default_clause = f"DEFAULT {1 if field.default else 0}"
                            else:
                                default_clause = f"DEFAULT {field.default}"
                        
                        try:
                            sql = f"ALTER TABLE {table._meta.table_name} ADD COLUMN {col_name} {field_type} {null_clause} {default_clause}"
                            db.execute_sql(sql)
                            migration_log.append(f"Added column: {table._meta.table_name}.{col_name}")
                        except Exception as e:
                            # Column might already exist or other error
                            print(f"Could not add column {col_name}: {e}")
        
        # Step 3: Ensure default themes exist and update built-in themes
        from src.core.database import get_default_themes
        default_themes = get_default_themes()
        
        for theme_name, theme_colors in default_themes.items():
            existing = Theme.select().where(Theme.name == theme_name).first()
            if not existing:
                Theme.create(
                    name=theme_name,
                    is_active=False,
                    is_custom=False,
                    **theme_colors
                )
                migration_log.append(f"Created default theme: {theme_name}")
            else:
                # Update built-in themes (not custom) with latest colors
                if not existing.is_custom:
                    # Check if any colors changed
                    colors_changed = False
                    for color_key, color_value in theme_colors.items():
                        if getattr(existing, color_key) != color_value:
                            colors_changed = True
                            setattr(existing, color_key, color_value)
                    
                    if colors_changed:
                        existing.save()
                        migration_log.append(f"Updated built-in theme colors: {theme_name}")
        
        # Step 4: Update database version
        set_database_version(app_version)
        migration_log.append(f"Updated database version to: {app_version}")
        
        db.close()
        
        if migration_log:
            message = "Migration completed successfully!\n\nChanges:\n" + "\n".join(f"• {log}" for log in migration_log)
        else:
            message = "Database checked - no migrations needed."
        
        return (True, message)
        
    except Exception as e:
        error_msg = f"Migration failed: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        return (False, error_msg)


def auto_migrate_on_startup():
    """
    Automatically run migrations on startup if enabled in config
    """
    try:
        auto_update = config.get('advanced.auto_update_database', True)
        
        if auto_update and needs_migration():
            print("Auto-updating database...")
            success, message = run_migrations()
            if success:
                print("Database auto-update completed")
            else:
                print(f"Database auto-update failed: {message}")
            return success
        
        return True
    except Exception as e:
        print(f"Error in auto-migrate: {e}")
        return False


def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    from datetime import datetime
    
    try:
        db_path = get_database_path()
        backup_path = db_path.parent / f"lifeboat_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return True, str(backup_path)
    except Exception as e:
        print(f"Backup failed: {e}")
        return False, str(e)
