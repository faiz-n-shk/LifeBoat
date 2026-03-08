"""
Stat Card Widget
Animated summary card for dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPixmap


class StatCard(QFrame):
    """Animated statistic card"""
    
    def __init__(self, title: str, icon_file: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_file = icon_file
        self._value = 0
        self._displayed_value = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup card UI"""
        from src.core.path_manager import get_resource_path
        
        self.setObjectName("stat-card")
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame#stat-card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(80, 80, 100, 0.3),
                    stop:1 rgba(60, 60, 80, 0.2));
                border: 1px solid rgba(100, 100, 120, 0.3);
                border-radius: 12px;
                padding: 4px;
            }
            QFrame#stat-card:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(90, 90, 110, 0.4),
                    stop:1 rgba(70, 70, 90, 0.3));
                border-color: rgba(100, 150, 255, 0.5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        from src.shared.icon_utils import load_themed_icon
        self.icon_label = QLabel()
        icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{self.icon_file}"), size=(40, 40))
        self.icon_label.setPixmap(icon_pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Value
        self.value_label = QLabel("0")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Title
        self.title_label = QLabel(self.title)
        font = QFont()
        font.setPointSize(10)
        self.title_label.setFont(font)
        self.title_label.setProperty("class", "secondary-text")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.setLayout(layout)
    
    def set_value(self, value, animate: bool = True):
        """Set card value with optional animation"""
        # Handle string values (like formatted currency)
        if isinstance(value, str):
            self._value = value
            self._displayed_value = value
            self.value_label.setText(value)
        else:
            # Handle numeric values with animation
            self._value = value
            
            if animate:
                self.animate_value()
            else:
                self._displayed_value = value
                self.value_label.setText(str(value))
    
    def animate_value(self):
        """Animate value change"""
        from src.core.config import config
        if not config.get('appearance.enable_animations', True):
            self._displayed_value = self._value
            self.value_label.setText(str(self._value))
            return
        
        self.animation = QPropertyAnimation(self, b"displayedValue")
        self.animation.setDuration(800)
        self.animation.setStartValue(self._displayed_value)
        self.animation.setEndValue(self._value)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
    
    @pyqtProperty(float)
    def displayedValue(self):
        return self._displayed_value
    
    @displayedValue.setter
    def displayedValue(self, value):
        self._displayed_value = value
        self.value_label.setText(str(int(value)))
    
    def reload_icon(self):
        """Reload icon with current theme"""
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_themed_icon
        icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{self.icon_file}"), size=(40, 40))
        self.icon_label.setPixmap(icon_pixmap)
