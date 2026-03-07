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
        self.title_container = QWidget()
        self.title_container.setFixedHeight(75)
        self.title_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        
        title_layout = QVBoxLayout(self.title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Top section with icon and text - themed with accent color
        self.top_section = QWidget()
        self.top_section.setObjectName("nav-title-section")
        
        top_layout = QHBoxLayout(self.top_section)
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
        self.title_label = QLabel("Lifeboat")
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
        self.title_label.setFont(font)
        self.title_label.setObjectName("nav-title-text")
        top_layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        top_layout.addStretch()
        
        title_layout.addWidget(self.top_section)
        
        # Apply theme styling
        self.apply_title_theme()
        
        # Subtle separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(100, 100, 120, 0.15);")
        title_layout.addWidget(separator)
        
        layout.addWidget(self.title_container)
        
        # Navigation items with SVG icons
        nav_items = [
            ("Dashboard", "feature_dashboard.svg"),
            ("Calendar", "feature_calendar.svg"),
            ("Expenses", "feature_expenses.svg"),
            ("Habits", "feature_habits.svg"),
            ("Notes", "feature_notes.svg"),
            ("Settings", "feature_settings.svg"),
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
        self.reload_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_reload.svg")))
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
        self.restart_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_restart.svg")))
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
        """Create navigation button with themed SVG icon"""
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_themed_icon
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
        
        btn = QPushButton(f"  {name}")
        
        # Load themed icon
        icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{icon}"), size=(20, 20))
        btn.setIcon(QIcon(icon_pixmap))
        btn.setIconSize(QSize(20, 20))
        btn.setObjectName("nav-button")
        btn.setProperty("active", False)
        btn.setProperty("icon_file", icon)  # Store for reloading
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add hover animation property
        btn._hover_offset = 0
        
        def get_hover_offset(self):
            return self._hover_offset
        
        def set_hover_offset(self, value):
            self._hover_offset = value
            # Update button style with offset
            self.setStyleSheet(f"""
                QPushButton {{
                    padding-left: {20 + value}px;
                }}
            """)
        
        # Bind methods to button
        btn.get_hover_offset = lambda: get_hover_offset(btn)
        btn.set_hover_offset = lambda v: set_hover_offset(btn, v)
        
        btn.clicked.connect(lambda: self.on_nav_click(name))
        return btn
    
    def reload_icons(self):
        """Reload all navigation icons with current theme"""
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_themed_icon
        from PyQt6.QtGui import QIcon
        
        # Reload navigation button icons
        for name, btn in self.buttons.items():
            icon_file = btn.property("icon_file")
            if icon_file:
                icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{icon_file}"), size=(20, 20))
                btn.setIcon(QIcon(icon_pixmap))
        
        # Reload title section theme
        self.apply_title_theme()
    
    def apply_title_theme(self):
        """Apply theme colors to the title section"""
        from src.core.theme_manager import theme_manager
        from src.core.database import db
        from src.models.theme import Theme
        
        try:
            db.connect(reuse_if_open=True)
            theme = Theme.get(Theme.name == theme_manager.current_theme)
            db.close()
            
            # Apply gradient background with accent color
            self.top_section.setStyleSheet(f"""
                QWidget#nav-title-section {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {theme.accent},
                        stop:1 {theme.accent_hover});
                }}
            """)
            
            # Set text color to contrast with accent
            self.title_label.setStyleSheet(f"""
                QLabel#nav-title-text {{
                    background: transparent;
                    color: {theme.bg_primary};
                    font-size: 18pt;
                }}
            """)
        except Exception as e:
            print(f"Error applying title theme: {e}")
    
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
