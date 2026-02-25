"""
Navigation Sidebar
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class NavigationSidebar(QWidget):
    """Navigation sidebar with feature buttons"""
    
    # Signal emitted when navigation item is clicked
    navigate_requested = pyqtSignal(str)
    
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
            ("Tasks", "✓"),
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
