"""
Main Application Class
"""
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

from src.core.constants import (
    APP_NAME, APP_VERSION,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
)
from src.core.config import config
from src.core.theme_manager import theme_manager
from src.ui.main_window import MainWindow


class LifeboatApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setup_window()
        
        # Load theme
        theme_manager.load_theme()
        
        # Create main window UI
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
    
    def setup_window(self):
        """Setup window size and position"""
        # Get saved dimensions or use defaults
        width = config.get('window.width', DEFAULT_WINDOW_WIDTH)
        height = config.get('window.height', DEFAULT_WINDOW_HEIGHT)
        
        self.resize(width, height)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Center window on screen
        if not config.get('window.remember_position', True):
            self.center_on_screen()
    
    def center_on_screen(self):
        """Center window on screen"""
        screen = self.screen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window size if enabled
        if config.get('window.remember_size', True):
            config.set('window.width', self.width())
            config.set('window.height', self.height())
            config.save()
        
        event.accept()
