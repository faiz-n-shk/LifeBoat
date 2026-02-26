"""
Lifeboat 2.0 - Personal Life Management Application
Main entry point
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.core.app import LifeboatApp
from src.core.database import initialize_database
from src.core.config import ensure_config_exists, config


def main():
    """Main entry point"""
    # Windows taskbar icon fix
    import sys
    import os
    if sys.platform == 'win32':
        try:
            # Set AppUserModelID to make taskbar icon work
            import ctypes
            myappid = 'fayz212.lifeboat.app.2'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
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
    ensure_config_exists()
    initialize_database()
    
    # Create and show main window
    window = LifeboatApp()
    
    # Check if should start minimized
    if config.get('behavior.start_minimized', False):
        # Start hidden in system tray
        window.hide()
    else:
        # Show window normally
        window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
