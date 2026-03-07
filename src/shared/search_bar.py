"""
Shared Search Bar Component
Search input with icon inside
"""
from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from src.core.path_manager import get_resource_path


class SearchBar(QLineEdit):
    """Search bar with icon inside"""
    
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(36)
        
        icon_label = QLabel(self)
        from src.shared.icon_utils import load_themed_icon
        icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_search.svg"), size=(16, 16))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setStyleSheet("background: transparent; border: none; padding: 0px;")
        icon_label.setFixedSize(20, 20)
        
        self.icon_label = icon_label
        self.update_icon_position()
        
        self.setStyleSheet("""
            QLineEdit {
                padding-left: 32px;
                padding-right: 10px;
                border-radius: 6px;
            }
        """)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_icon_position()
    
    def update_icon_position(self):
        self.icon_label.move(8, (self.height() - self.icon_label.height()) // 2)
