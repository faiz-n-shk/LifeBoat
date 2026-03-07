"""
Debug and logging utilities
Centralized debug output management for development

═══════════════════════════════════════════════════════════════════════════════
                            MASTER DEBUG CONTROL
═══════════════════════════════════════════════════════════════════════════════

QUICK START:
    - Set DEBUG_ENABLED = True  → See all logs in terminal (development mode)
    - Set DEBUG_ENABLED = False → Clean terminal, no logs (production mode)

WHAT IT CONTROLS:
    ✓ Python logging (logger.info, logger.error, etc.)
    ✓ Debug prints (debug_log() calls)
    ✓ All console output from the application

AUTOMATIC BEHAVIOR:
    - Automatically disabled when app is frozen (PyInstaller build)
    - Can be toggled at runtime using DebugLogger.enable_all() / disable_all()

USAGE EXAMPLES:
    # In any file:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("This will only show if DEBUG_ENABLED = True")
    
    # Or use debug_log:
    from src.core.debug import debug_log
    debug_log('MyCategory', 'This message')

═══════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import logging


# ════════════════════════════════════════════════════════════════════════════
# MASTER DEBUG SWITCH - CHANGE THIS VALUE
# ════════════════════════════════════════════════════════════════════════════
DEBUG_ENABLED = False  # Set to False for clean terminal (no logs)
# ════════════════════════════════════════════════════════════════════════════


def configure_logging():
    """Configure Python logging based on DEBUG_ENABLED setting"""
    if DEBUG_ENABLED:
        # Enable logging with detailed output
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # Override any existing configuration
        )
    else:
        # Disable all logging output (only show CRITICAL errors)
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(message)s',
            handlers=[
                logging.NullHandler()
            ],
            force=True
        )
        # Disable all existing loggers
        logging.getLogger().setLevel(logging.CRITICAL)


class DebugLogger:
    """Centralized debug logger for development"""
    
    # Debug categories - can be toggled individually (only works if DEBUG_ENABLED = True)
    CATEGORIES = {
        'PathManager': True,
        'Config': True,
        'Database': True,
        'ActivityLogger': True,
        'ThemeManager': True,
        'General': True,
    }
    
    @classmethod
    def is_enabled(cls, category='General'):
        """Check if debug is enabled for a category"""
        if not DEBUG_ENABLED:
            return False
        return cls.CATEGORIES.get(category, True)
    
    @classmethod
    def log(cls, category, message):
        """Log a debug message"""
        if cls.is_enabled(category):
            print(f"[{category}] {message}")
    
    @classmethod
    def disable_all(cls):
        """Disable all debug output"""
        global DEBUG_ENABLED
        DEBUG_ENABLED = False
        configure_logging()
    
    @classmethod
    def enable_all(cls):
        """Enable all debug output"""
        global DEBUG_ENABLED
        DEBUG_ENABLED = True
        configure_logging()
    
    @classmethod
    def disable_category(cls, category):
        """Disable debug output for a specific category"""
        if category in cls.CATEGORIES:
            cls.CATEGORIES[category] = False
    
    @classmethod
    def enable_category(cls, category):
        """Enable debug output for a specific category"""
        if category in cls.CATEGORIES:
            cls.CATEGORIES[category] = True


# Convenience function
def debug_log(category, message):
    """Convenience function for debug logging"""
    DebugLogger.log(category, message)


# Check if running in production mode
def is_production():
    """Check if app is running in production mode (frozen by PyInstaller)"""
    return getattr(sys, 'frozen', False)


# Auto-disable debug in production
if is_production():
    DEBUG_ENABLED = False


# Configure logging on module import
configure_logging()
