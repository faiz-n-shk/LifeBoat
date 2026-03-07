"""
Main Window UI
Contains navigation and content area
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt

from src.ui.navigation import NavigationSidebar
from src.ui.content_area import ContentArea
from src.features.dashboard.view import DashboardView


class MainWindow(QWidget):
    """Main window containing navigation and content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.register_features()
        self.connect_signals()
        
        # Show dashboard by default
        self.content.show_feature("Dashboard")
    
    def setup_ui(self):
        """Setup main window UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation sidebar
        self.navigation = NavigationSidebar(self)
        layout.addWidget(self.navigation)
        
        # Vertical separator line
        from PyQt6.QtWidgets import QFrame
        self.separator = QFrame()
        self.separator.setFixedWidth(1)
        self.update_separator_color()
        layout.addWidget(self.separator)
        
        # Content area
        self.content = ContentArea(self)
        layout.addWidget(self.content, 1)
        
        self.setLayout(layout)
    
    def update_separator_color(self):
        """Update separator color based on current theme"""
        from src.core.theme_manager import theme_manager
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        if theme:
            self.separator.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.border};
                    border: none;
                }}
            """)
    
    def register_features(self):
        """Register all feature modules"""
        # Dashboard
        dashboard = DashboardView()
        self.content.register_feature("Dashboard", dashboard)
        
        # Calendar
        from src.features.calendar.view import CalendarView
        calendar_view = CalendarView()
        self.content.register_feature("Calendar", calendar_view)
        
        # Expenses
        from src.features.expenses.view import ExpensesView
        expenses = ExpensesView()
        self.content.register_feature("Expenses", expenses)
        
        # Habits
        from src.features.habits.view import HabitsView
        habits = HabitsView()
        self.content.register_feature("Habits", habits)
        
        # Notes
        from src.features.notes.view import NotesView
        notes = NotesView()
        self.content.register_feature("Notes", notes)
        
        # Settings
        from src.features.settings.view import SettingsView
        settings = SettingsView()
        self.content.register_feature("Settings", settings)
    
    def connect_signals(self):
        """Connect navigation signals"""
        self.navigation.navigate_requested.connect(self.on_navigate)
        self.navigation.reload_requested.connect(self.on_reload)
        self.navigation.restart_requested.connect(self.on_restart)
        
        # Connect config signals for hot-loading
        from src.core.config import config
        config.signals.appearance_changed.connect(self.on_appearance_changed)
        config.signals.locale_changed.connect(self.on_locale_changed)
        config.signals.advanced_changed.connect(self.on_advanced_changed)
        config.signals.restart_requested.connect(self.on_restart)

    
    def on_navigate(self, feature_name: str):
        """Handle navigation request"""
        # Check for unsaved changes in settings
        current_feature = self.content.current_feature
        if current_feature == "Settings":
            settings_view = self.content.get_feature_widget("Settings")
            if settings_view and hasattr(settings_view, 'check_unsaved_changes'):
                if not settings_view.check_unsaved_changes():
                    # User cancelled navigation
                    return
        
        # Navigation confirmed, update UI
        self.content.show_feature(feature_name)
        self.navigation.set_active(feature_name)
    
    def on_reload(self):
        """Handle reload request - reload app and go to dashboard"""
        # Reload theme
        from src.core.theme_manager import theme_manager
        theme_manager.load_theme()
        
        # Refresh all features
        self.content.refresh_all_features()
        
        # Navigate to dashboard
        self.navigation.set_active("Dashboard")
        self.content.show_feature("Dashboard")
    
    def on_restart(self):
        """Handle restart request"""
        import sys
        import os
        import subprocess
        from PyQt6.QtWidgets import QApplication
        
        # Close the current application
        QApplication.instance().quit()
        
        # Check if running as packaged app or script
        if getattr(sys, 'frozen', False):
            # Running as packaged executable
            executable = sys.executable
            if os.name == 'nt':  # Windows
                # Use CREATE_NO_WINDOW to prevent console window
                subprocess.Popen([executable], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([executable])
        else:
            # Running as script
            python = sys.executable
            script = sys.argv[0]
            if os.name == 'nt':  # Windows
                # Use pythonw.exe if available to avoid console window
                pythonw = python.replace('python.exe', 'pythonw.exe')
                if os.path.exists(pythonw):
                    subprocess.Popen([pythonw, script])
                else:
                    subprocess.Popen([python, script], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([python, script])
    
    def on_appearance_changed(self):
        """Handle appearance settings change"""
        # Reload theme with new font settings
        from src.core.theme_manager import theme_manager
        theme_manager.load_theme()
        
        # Update separator color
        self.update_separator_color()
        
        # Reload navigation icons with new theme
        self.navigation.reload_icons()
        
        # Refresh all registered features to apply new theme/font
        self.content.refresh_all_features()
    
    def on_locale_changed(self):
        """Handle locale settings change"""
        # Refresh all registered features to apply new formats
        self.content.refresh_all_features()
    
    def on_advanced_changed(self):
        """Handle advanced settings change"""
        # Update debug buttons visibility in navigation
        self.navigation.update_debug_buttons_visibility()
