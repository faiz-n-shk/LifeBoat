"""
Lifeboat 2.0 - Personal Life Management Application
Main entry point
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

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
