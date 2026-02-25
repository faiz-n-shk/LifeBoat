"""
Main Window UI
Contains navigation and content area
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
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
        
        # Content area
        self.content = ContentArea(self)
        layout.addWidget(self.content, 1)
        
        self.setLayout(layout)
    
    def register_features(self):
        """Register all feature modules"""
        # Dashboard
        dashboard = DashboardView()
        self.content.register_feature("Dashboard", dashboard)
        
        # Calendar
        from src.features.calendar.view import CalendarView
        calendar_view = CalendarView()
        self.content.register_feature("Calendar", calendar_view)
        
        # Tasks
        from src.features.tasks.view import TasksView
        tasks = TasksView()
        self.content.register_feature("Tasks", tasks)
        
        # Expenses
        from src.features.expenses.view import ExpensesView
        expenses = ExpensesView()
        self.content.register_feature("Expenses", expenses)
        
        # Settings
        from src.features.settings.view import SettingsView
        settings = SettingsView()
        self.content.register_feature("Settings", settings)
        
        # TODO: Register other features as they're implemented
    
    def connect_signals(self):
        """Connect navigation signals"""
        self.navigation.navigate_requested.connect(self.on_navigate)
        
        # Connect config signals for hot-loading
        from src.core.config import config
        config.signals.appearance_changed.connect(self.on_appearance_changed)
        config.signals.locale_changed.connect(self.on_locale_changed)

    
    def on_navigate(self, feature_name: str):
        """Handle navigation request"""
        self.navigation.set_active(feature_name)
        self.content.show_feature(feature_name)
    
    def on_appearance_changed(self):
        """Handle appearance settings change"""
        # Reload theme with new font settings
        from src.core.theme_manager import theme_manager
        theme_manager.load_theme()
        
        # Refresh all registered features to apply new theme/font
        self.content.refresh_all_features()
    
    def on_locale_changed(self):
        """Handle locale settings change"""
        # Refresh all registered features to apply new formats
        self.content.refresh_all_features()
