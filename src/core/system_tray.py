"""
System Tray Icon Manager
Handles system tray icon, menu, and window minimize/restore behavior
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.path_manager import get_resource_path
from src.core.config import config


class SystemTrayManager(QObject):
    """Manages system tray icon and interactions"""
    
    # Signals
    show_window_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.tray_menu = None
        self.window = parent
        self.setup_tray()
    
    def setup_tray(self):
        """Setup system tray icon and menu"""
        # Create tray icon
        icon_path = get_resource_path("assets/lifeboat.ico")
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self.parent())
        
        # Create tray menu
        self.tray_menu = QMenu()
        
        # Show/Hide action
        self.show_action = QAction("Show Lifeboat", self)
        self.show_action.triggered.connect(self.on_show_window)
        self.tray_menu.addAction(self.show_action)
        
        self.tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.on_quit)
        self.tray_menu.addAction(quit_action)
        
        # Set menu and connect signals
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Set tooltip
        self.tray_icon.setToolTip("Lifeboat - Personal Life Manager")
        
        # Show tray icon if enabled
        self.update_tray_visibility()
    
    def update_tray_visibility(self):
        """Update tray icon visibility based on settings"""
        # Show tray icon if any tray-related feature is enabled
        minimize_to_tray = config.get('behavior.minimize_to_tray', False)
        close_to_tray = config.get('behavior.close_to_tray', False)
        start_minimized = config.get('behavior.start_minimized', False)
        
        if minimize_to_tray or close_to_tray or start_minimized:
            self.tray_icon.show()
        else:
            self.tray_icon.hide()
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle window visibility
            self.on_show_window()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.on_show_window()
    
    def on_show_window(self):
        """Show and restore the main window"""
        self.show_window_requested.emit()
    
    def on_quit(self):
        """Quit the application"""
        self.quit_requested.emit()
    
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show a system tray notification"""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, 3000)
    
    def cleanup(self):
        """Cleanup tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
    
    def hide(self):
        """Hide the tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
