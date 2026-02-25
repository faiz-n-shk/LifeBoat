"""
Habits View
Habit tracking and streaks
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class HabitsView(QWidget):
    """Habits view - Coming Soon"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup habits UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("🔄 Habits")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Coming soon message
        message = QLabel("Coming Soon")
        message.setProperty("class", "secondary-text")
        font2 = QFont()
        font2.setPointSize(16)
        message.setFont(font2)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh view"""
        pass
