"""
Lifeboat v2 - Personal Life Management Application
Main entry point
"""
import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QSharedMemory
from PyQt6.QtGui import QIcon

# Import debug configuration FIRST to set up logging
from src.core.debug import DEBUG_ENABLED

from src.core.app import LifeboatApp
from src.core.database import initialize_database
from src.core.config import ensure_config_exists, config


# Setup error logs directory
ERROR_LOGS_DIR = Path(__file__).parent / "errorLogs"
ERROR_LOGS_DIR.mkdir(exist_ok=True)

# Configure logging with both file and console handlers
log_handlers = [
    # Always log errors to file (even in production)
    logging.FileHandler(ERROR_LOGS_DIR / "error.log", encoding='utf-8')
]

# Add console handler only if DEBUG_ENABLED
if DEBUG_ENABLED:
    log_handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO if DEBUG_ENABLED else logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers,
    force=True
)

logger = logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to log unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupt to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Always log critical errors to file regardless of DEBUG_ENABLED
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error dialog to user (always show for critical errors)
    try:
        error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}\n\nError details have been saved to errorLogs/error.log"
        QMessageBox.critical(None, "Critical Error", error_msg)
    except:
        pass  # If we can't show dialog, just log it


# Set global exception handler
sys.excepthook = handle_exception


def main():
    """Main entry point"""
    logger.info("Starting Lifeboat application...")
    
    # Windows taskbar icon fix
    import sys
    import os
    if sys.platform == 'win32':
        try:
            # Set AppUserModelID to make taskbar icon work
            import ctypes
            myappid = 'fayz212.lifeboat.app.2'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            logger.debug("Set Windows AppUserModelID")
        except Exception as e:
            logger.warning(f"Could not set AppUserModelID: {e}")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Single instance check
    shared_memory = QSharedMemory("LifeboatApp_SingleInstance")
    
    if not shared_memory.create(1):
        # Another instance is already running
        logger.info("Another instance detected")
        reply = QMessageBox.question(
            None,
            "Lifeboat Already Running",
            "An instance of Lifeboat is already running.\n\nWhat would you like to do?",
            QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Open
        )
        
        if reply == QMessageBox.StandardButton.Open:
            logger.info("User chose to open existing instance")
            sys.exit(0)
        elif reply == QMessageBox.StandardButton.Ignore:
            logger.warning("User chose to run multiple instances")
            shared_memory.detach()
        else:
            logger.info("User cancelled")
            sys.exit(0)
    app.setApplicationName("Lifeboat")
    app.setOrganizationName("Fayz212")
    
    # Set application icon (for all windows and dialogs)
    from src.core.path_manager import get_resource_path, path_manager
    icon_path = get_resource_path("assets/lifeboat.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    # Load bundled fonts from assets/fonts
    from PyQt6.QtGui import QFontDatabase
    fonts_dir = get_resource_path("assets/fonts")
    if os.path.exists(fonts_dir):
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(fonts_dir, filename)
                QFontDatabase.addApplicationFont(font_path)
    
    # Load user-imported fonts from user fonts directory
    user_fonts_dir = path_manager.get_user_fonts_dir()
    if os.path.exists(user_fonts_dir):
        for filename in os.listdir(user_fonts_dir):
            if filename.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(user_fonts_dir, filename)
                QFontDatabase.addApplicationFont(font_path)
    
    # Initialize configuration and database
    logger.info("Initializing configuration and database...")
    ensure_config_exists()
    initialize_database()
    
    # Auto-migrate database if enabled
    logger.info("Checking for database migrations...")
    from src.core.database_migrations import auto_migrate_on_startup
    auto_migrate_on_startup()
    
    # Create and show main window
    logger.info("Creating main window...")
    window = LifeboatApp()
    
    # Check if should start minimized
    if config.get('behavior.start_minimized', False):
        logger.info("Starting minimized to system tray")
        window.hide()
    else:
        logger.info("Showing main window")
        window.show()
    
    # Run application
    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
