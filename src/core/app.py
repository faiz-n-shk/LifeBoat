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
        
        # Track resize state
        self.programmatic_resize = False
        self.resize_timer = None
    
    def setup_window(self):
        """Setup window size and position"""
        # Get saved resolution setting
        resolution = config.get('window.resolution', 'custom')
        
        if resolution != 'custom':
            # Apply preset resolution
            try:
                width, height = map(int, resolution.split('x'))
                self.programmatic_resize = True
                self.resize(width, height)
            except:
                # Fallback to saved or default dimensions
                width = config.get('window.width', DEFAULT_WINDOW_WIDTH)
                height = config.get('window.height', DEFAULT_WINDOW_HEIGHT)
                self.resize(width, height)
        else:
            # Use saved dimensions or defaults
            width = config.get('window.width', DEFAULT_WINDOW_WIDTH)
            height = config.get('window.height', DEFAULT_WINDOW_HEIGHT)
            self.resize(width, height)
        
        # Get minimum size from constants
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
    
    def resizeEvent(self, event):
        """Handle window resize event"""
        super().resizeEvent(event)
        
        # Skip if this is a programmatic resize
        if self.programmatic_resize:
            self.programmatic_resize = False
            return
        
        # User manually resized - check if it matches a preset
        current_res = config.get('window.resolution', 'custom')
        
        if current_res != 'custom':
            # Check if new size matches the preset resolution
            try:
                preset_width, preset_height = map(int, current_res.split('x'))
                current_width = self.width()
                current_height = self.height()
                
                # Allow small tolerance (10px) for window decorations
                if abs(current_width - preset_width) > 10 or abs(current_height - preset_height) > 10:
                    # Size doesn't match preset, switch to custom
                    config.set('window.resolution', 'custom')
                    config.save()
                    
                    # Update the UI if settings page is open
                    self.update_settings_resolution_display()
            except:
                pass
    
    def update_settings_resolution_display(self):
        """Update the resolution display in settings if it's open"""
        try:
            # Get the settings view
            content_area = self.main_window.content
            settings_view = content_area.get_feature_widget("Settings")
            
            if settings_view and hasattr(settings_view, 'appearance_section'):
                appearance_section = settings_view.appearance_section
                if hasattr(appearance_section, 'update_resolution_display'):
                    appearance_section.update_resolution_display()
        except Exception as e:
            print(f"Error updating settings display: {e}")
