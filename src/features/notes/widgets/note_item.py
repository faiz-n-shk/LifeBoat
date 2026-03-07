"""
Note Item Widget
Individual note card in the list
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from src.shared.formatters import format_datetime


class NoteItem(QFrame):
    """Widget representing a single note"""
    
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    pin_clicked = pyqtSignal(int)
    
    def __init__(self, note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setup_ui()
    
    def setup_ui(self):
        """Setup note item UI"""
        self.setObjectName("note-item")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Header: Title with pin indicator
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Pin indicator
        if self.note.pinned:
            from src.core.path_manager import get_resource_path
            from PyQt6.QtGui import QPixmap
            
            pin_icon = QLabel()
            icon_pixmap = QPixmap(get_resource_path("assets/icons/icon_pinned.svg"))
            pin_icon.setPixmap(icon_pixmap.scaled(14, 14, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            pin_icon.setFixedWidth(18)
            header_layout.addWidget(pin_icon)
        
        # Title
        title = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        header_layout.addWidget(title, 1)
        
        layout.addLayout(header_layout)
        
        # Content preview (first 200 characters)
        content_preview = self.note.content[:200]
        if len(self.note.content) > 200:
            content_preview += "..."
        
        content_label = QLabel(content_preview)
        content_label.setWordWrap(True)
        content_label.setProperty("class", "secondary-text")
        font = QFont()
        font.setPointSize(9)
        content_label.setFont(font)
        layout.addWidget(content_label)
        
        # Footer: Tags, date, and actions
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)
        
        # Tags
        if self.note.tags:
            tags_text = " ".join([f"#{tag.strip()}" for tag in self.note.tags.split(',') if tag.strip()])
            tags_label = QLabel(tags_text)
            tags_label.setProperty("class", "accent-label")
            font = QFont()
            font.setPointSize(8)
            tags_label.setFont(font)
            footer_layout.addWidget(tags_label)
        
        footer_layout.addStretch()
        
        # Updated date
        date_label = QLabel(format_datetime(self.note.updated_at))
        date_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(8)
        date_label.setFont(font)
        footer_layout.addWidget(date_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)
        
        from src.core.path_manager import get_resource_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        pin_btn = QPushButton()
        pin_icon = "icon_pinned.svg" if self.note.pinned else "icon_pin.svg"
        pin_btn.setIcon(QIcon(get_resource_path(f"assets/icons/{pin_icon}")))
        pin_btn.setIconSize(QSize(16, 16))
        pin_btn.setFixedSize(28, 28)
        pin_btn.setToolTip("Unpin" if self.note.pinned else "Pin")
        pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pin_btn.clicked.connect(lambda: self.pin_clicked.emit(self.note.id))
        actions_layout.addWidget(pin_btn)
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_edit.svg")))
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.note.id))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_delete.svg")))
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setFixedSize(28, 28)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.note.id))
        actions_layout.addWidget(delete_btn)
        
        footer_layout.addLayout(actions_layout)
        
        layout.addLayout(footer_layout)
        
        self.setLayout(layout)



