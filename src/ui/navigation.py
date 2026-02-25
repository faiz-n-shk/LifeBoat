"""
Navigation Sidebar
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from src.core.constants import APP_VERSION


class NavigationSidebar(QWidget):
    """Navigation sidebar with feature buttons"""
    
    # Signal emitted when navigation item is clicked
    navigate_requested = pyqtSignal(str)
    reload_requested = pyqtSignal()
    restart_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_button = None
        self.buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup navigation UI"""
        self.setFixedWidth(250)
        self.setObjectName("navigation")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title
        title = QLabel("⛵ Lifeboat")
        title.setObjectName("app-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(60)
        layout.addWidget(title)
        
        # Navigation items
        nav_items = [
            ("Dashboard", "📊"),
            ("Calendar", "📅"),
            ("Tasks", "☑"),
            ("Expenses", "💰"),
            ("Goals", "🎯"),
            ("Habits", "🔄"),
            ("Notes", "📝"),
            ("Settings", "⚙"),
        ]
        
        for name, icon in nav_items:
            btn = self.create_nav_button(name, icon)
            self.buttons[name] = btn
            layout.addWidget(btn)
        
        # Spacer
        layout.addStretch()
        
        # Bottom section with buttons and version
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(10, 5, 10, 10)
        bottom_layout.setSpacing(4)
        
        from PyQt6.QtCore import QSize
        from PyQt6.QtWidgets import QSizePolicy
        from src.core.theme_manager import theme_manager
        
        # Get theme colors for warning/danger
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        if not theme:
            # Fallback colors if theme not found
            warning_color = "#ffc107"
            danger_color = "#dc3545"
        else:
            warning_color = theme.warning
            danger_color = theme.danger
        
        # Reload button (small, circular, warning color)
        self.reload_btn = QPushButton()
        self.reload_btn.setIcon(QIcon("assets/icons/reload.svg"))
        self.reload_btn.setFixedSize(20, 20)
        self.reload_btn.setIconSize(QSize(16, 16))
        self.reload_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.reload_btn.setToolTip("Reload")
        self.reload_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 10px;
                padding: 0px;
                margin: 0px;
                background-color: {warning_color};
                border: none;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {warning_color};
                opacity: 0.8;
            }}
        """)
        self.reload_btn.clicked.connect(self.on_reload)
        bottom_layout.addWidget(self.reload_btn, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Restart button (small, circular, danger color)
        self.restart_btn = QPushButton()
        self.restart_btn.setIcon(QIcon("assets/icons/restart.svg"))
        self.restart_btn.setFixedSize(20, 20)
        self.restart_btn.setIconSize(QSize(16, 16))
        self.restart_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.restart_btn.setToolTip("Restart")
        self.restart_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 10px;
                padding: 0px;
                margin: 0px;
                background-color: {danger_color};
                border: none;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {danger_color};
                opacity: 0.8;
            }}
        """)
        self.restart_btn.clicked.connect(self.on_restart)
        bottom_layout.addWidget(self.restart_btn, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Spacer to push version to center
        bottom_layout.addStretch()
        
        # Version label (centered)
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setProperty("class", "small-text")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(version_label)
        
        # Spacer on right to keep version centered
        bottom_layout.addStretch()
        
        # Invisible spacer widget to balance the buttons on the left (20px + 4px spacing + 20px = 44px)
        self.spacer_widget = QWidget()
        self.spacer_widget.setFixedWidth(44)
        bottom_layout.addWidget(self.spacer_widget)
        
        # Check config to show/hide debug buttons (after all widgets are created)
        from src.core.config import config
        show_debug = config.get('advanced.show_debug_buttons', False)
        self.reload_btn.setVisible(show_debug)
        self.restart_btn.setVisible(show_debug)
        self.spacer_widget.setVisible(show_debug)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # Set Dashboard as active by default
        self.set_active("Dashboard")
    
    def create_nav_button(self, name: str, icon: str) -> QPushButton:
        """Create navigation button"""
        btn = QPushButton(f"{icon}  {name}")
        btn.setObjectName("nav-button")
        btn.setProperty("active", False)
        btn.setFixedHeight(50)
        btn.clicked.connect(lambda: self.on_nav_click(name))
        return btn
    
    def on_nav_click(self, name: str):
        """Handle navigation button click"""
        self.set_active(name)
        self.navigate_requested.emit(name)
    
    def set_active(self, name: str):
        """Set active navigation button"""
        # Deactivate previous button
        if self.active_button:
            self.active_button.setProperty("active", False)
            self.active_button.style().unpolish(self.active_button)
            self.active_button.style().polish(self.active_button)
        
        # Activate new button
        if name in self.buttons:
            self.active_button = self.buttons[name]
            self.active_button.setProperty("active", True)
            self.active_button.style().unpolish(self.active_button)
            self.active_button.style().polish(self.active_button)
    
    def on_reload(self):
        """Handle reload button click"""
        self.reload_requested.emit()
    
    def on_restart(self):
        """Handle restart button click"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Confirm Restart",
            "Are you sure you want to restart the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.restart_requested.emit()
    
    def update_debug_buttons_visibility(self):
        """Update debug buttons visibility based on config"""
        from src.core.config import config
        show_debug = config.get('advanced.show_debug_buttons', False)
        if hasattr(self, 'reload_btn'):
            self.reload_btn.setVisible(show_debug)
        if hasattr(self, 'restart_btn'):
            self.restart_btn.setVisible(show_debug)
        if hasattr(self, 'spacer_widget'):
            self.spacer_widget.setVisible(show_debug)
