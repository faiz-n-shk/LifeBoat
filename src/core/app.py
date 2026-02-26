"""
Main Application Class
"""
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.core.constants import (
    APP_NAME, APP_VERSION,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
)
from src.core.config import config
from src.core.theme_manager import theme_manager
from src.core.system_tray import SystemTrayManager
from src.ui.main_window import MainWindow


class LifeboatApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set application icon
        from src.core.path_manager import get_resource_path
        icon_path = get_resource_path("assets/lifeboat.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        # Load theme before creating UI
        theme_manager.load_theme()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setup_window()
        
        # Create main window UI
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
        
        # Track resize state
        self.programmatic_resize = False
        self.resize_timer = None
        
        # Initialize system tray
        self.tray_manager = SystemTrayManager(self)
        self.tray_manager.show_window_requested.connect(self.show_from_tray)
        self.tray_manager.quit_requested.connect(self.quit_application)
    
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
        # Check if close button should minimize to tray
        if config.get('behavior.close_to_tray', False):
            event.ignore()
            self.hide()
            return
        
        # Save window size if enabled
        if config.get('window.remember_size', True):
            config.set('window.width', self.width())
            config.set('window.height', self.height())
            config.save()
        
        # Quit application
        self.quit_application()
    
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
    
    def changeEvent(self, event):
        """Handle window state changes"""
        super().changeEvent(event)
        
        # Check if window was minimized and minimize to tray is enabled
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized() and config.get('behavior.minimize_to_tray', False):
                # Hide window to tray
                self.hide()
                event.ignore()
    
    def show_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()
    
    def quit_application(self):
        """Quit the application properly"""
        # Save window size if enabled
        if config.get('window.remember_size', True):
            config.set('window.width', self.width())
            config.set('window.height', self.height())
            config.save()
        
        # Hide tray icon
        if hasattr(self, 'tray_manager'):
            self.tray_manager.hide()
        
        # Quit application
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
