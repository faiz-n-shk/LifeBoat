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
        
        # App title with icon - clean modern design
        title_container = QWidget()
        title_container.setFixedHeight(75)
        title_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Top section with icon and text
        top_section = QWidget()
        top_section.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.2),
                    stop:1 rgba(50, 50, 70, 0.1));
            }
        """)
        
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(15, 15, 15, 15)
        top_layout.setSpacing(12)
        
        # App icon
        from src.core.path_manager import get_resource_path
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt as QtCore
        
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        icon_pixmap = QPixmap(get_resource_path("assets/icons/lifeboat.svg"))
        icon_label.setPixmap(icon_pixmap.scaled(50, 50, QtCore.AspectRatioMode.KeepAspectRatio, QtCore.TransformationMode.SmoothTransformation))
        top_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # App title text
        title = QLabel("Lifeboat")
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
        title.setFont(font)
        title.setStyleSheet("background: transparent; color: rgba(255, 255, 255, 0.95); font-size: 18pt;")
        top_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)
        
        top_layout.addStretch()
        
        title_layout.addWidget(top_section)
        
        # Subtle separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(100, 100, 120, 0.15);")
        title_layout.addWidget(separator)
        
        layout.addWidget(title_container)
        
        # Navigation items
        nav_items = [
            ("Dashboard", "📊"),
            ("Calendar", "📅"),
            ("Tasks", "☑"),
            ("Todos", "✓"),
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
        
        # Bottom section with debug buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(8, 4, 8, 4)
        bottom_layout.setSpacing(4)
        
        from PyQt6.QtCore import QSize
        from PyQt6.QtWidgets import QSizePolicy
        from src.core.theme_manager import theme_manager
        
        # Get theme colors for warning/danger
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        if not theme:
            warning_color = "#ffc107"
            danger_color = "#dc3545"
        else:
            warning_color = theme.warning
            danger_color = theme.danger
        
        # Reload button (small circle)
        self.reload_btn = QPushButton()
        from src.core.path_manager import get_resource_path
        self.reload_btn.setIcon(QIcon(get_resource_path("assets/icons/reload.svg")))
        self.reload_btn.setFixedSize(20, 20)
        self.reload_btn.setIconSize(QSize(12, 12))
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
        
        # Restart button (small circle)
        self.restart_btn = QPushButton()
        self.restart_btn.setIcon(QIcon(get_resource_path("assets/icons/restart.svg")))
        self.restart_btn.setFixedSize(20, 20)
        self.restart_btn.setIconSize(QSize(12, 12))
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
        
        # Add stretch to push buttons to far left
        bottom_layout.addStretch()
        
        # Check config to show/hide debug buttons
        from src.core.config import config
        show_debug = config.get('advanced.show_debug_buttons', False)
        self.reload_btn.setVisible(show_debug)
        self.restart_btn.setVisible(show_debug)
        
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
        # Emit navigation request first, let MainWindow decide if navigation is allowed
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
        from src.shared.dialogs import create_message_box
        from PyQt6.QtWidgets import QMessageBox
        
        msg = create_message_box(
            self,
            "Confirm Restart",
            "Are you sure you want to restart the application?",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.restart_requested.emit()
    
    def update_debug_buttons_visibility(self):
        """Update debug buttons visibility based on config"""
        from src.core.config import config
        show_debug = config.get('advanced.show_debug_buttons', False)
        
        # reload and restart buttons are only visible in debug mode, rebuild UI
        if hasattr(self, 'reload_btn'):
            self.reload_btn.setVisible(show_debug)
        if hasattr(self, 'restart_btn'):
            self.restart_btn.setVisible(show_debug)
