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
from src.core.config import ensure_config_exists


def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Lifeboat")
    app.setOrganizationName("Fayz212")
    
    # Set application icon (for all windows and dialogs)
    app.setWindowIcon(QIcon("assets/lifeboat.ico"))
    
    # Load custom fonts from assets/fonts
    from PyQt6.QtGui import QFontDatabase
    import os
    fonts_dir = "assets/fonts"
    if os.path.exists(fonts_dir):
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(fonts_dir, filename)
                QFontDatabase.addApplicationFont(font_path)
    
    # Initialize configuration and database
    ensure_config_exists()
    initialize_database()
    
    # Create and show main window
    window = LifeboatApp()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
