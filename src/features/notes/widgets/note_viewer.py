"""
Note Viewer
Read-only viewer for notes
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextBrowser, QCheckBox, QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextDocument

from src.shared.dialogs import BaseDialog
from src.shared.formatters import format_datetime


class NoteViewer(BaseDialog):
    """Read-only viewer for notes"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    pin_toggled = pyqtSignal(int)
    
    def __init__(self, parent=None, note=None, controller=None):
        self.note = note
        self.controller = controller
        
        super().__init__(parent, note.title if note else "Note", width=700, height=600)
        self.setup_content()
        self.add_action_buttons()
    
    def setup_content(self):
        """Setup viewer content"""
        # Header with title and metadata
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        
        # Pin indicator
        if self.note.pinned:
            pin_label = QLabel("📌")
            font = QFont()
            font.setPointSize(16)
            pin_label.setFont(font)
            header_layout.addWidget(pin_label)
        
        self.layout.addLayout(header_layout)
        
        # Metadata
        meta_layout = QHBoxLayout()
        
        created_label = QLabel(f"Created: {format_datetime(self.note.created_at)}")
        created_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        created_label.setFont(font)
        meta_layout.addWidget(created_label)
        
        meta_layout.addStretch()
        
        updated_label = QLabel(f"Updated: {format_datetime(self.note.updated_at)}")
        updated_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        updated_label.setFont(font)
        meta_layout.addWidget(updated_label)
        
        self.layout.addLayout(meta_layout)
        
        # Tags
        if self.note.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(6)
            
            tags_title = QLabel("Tags:")
            font = QFont()
            font.setPointSize(9)
            font.setBold(True)
            tags_title.setFont(font)
            tags_layout.addWidget(tags_title)
            
            for tag in self.note.tags.split(','):
                tag = tag.strip()
                if tag:
                    tag_pill = QLabel(f"#{tag}")
                    font = QFont()
                    font.setPointSize(8)
                    font.setBold(True)
                    tag_pill.setFont(font)
                    tag_pill.setStyleSheet("""
                        QLabel {
                            padding: 0.3em 0.8em;
                            border-radius: 10px;
                            background-color: rgba(100, 150, 255, 0.2);
                            border: 1px solid rgba(100, 150, 255, 0.4);
                            color: rgba(100, 150, 255, 1.0);
                        }
                    """)
                    tags_layout.addWidget(tag_pill)
            
            tags_layout.addStretch()
            self.layout.addLayout(tags_layout)
        
        # Content viewer - Use QTextBrowser for better HTML rendering
        from PyQt6.QtWidgets import QTextBrowser
        self.content_viewer = QTextBrowser()
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setPlainText(self.note.content)
        self.content_viewer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.content_viewer.setOpenExternalLinks(True)
        
        # Apply theme styling
        self._apply_content_styling()
        
        self.layout.addWidget(self.content_viewer, 1)
    
    def _apply_content_styling(self):
        """Apply theme styling to content viewer"""
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.content_viewer.setStyleSheet(f"""
                    QTextBrowser {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 12px 16px;
                        font-size: 11pt;
                        line-height: 1.6;
                    }}
                    QTextBrowser::corner {{
                        background-color: {theme_obj.bg_tertiary};
                        border: 1px solid {theme_obj.border};
                    }}
                """)
                db.close()
            except:
                pass
    
    def add_action_buttons(self):
        """Add action buttons at the bottom"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Pin/Unpin button
        pin_text = "📍 Unpin" if self.note.pinned else "📌 Pin"
        self.pin_btn = QPushButton(pin_text)
        self.pin_btn.setMinimumWidth(100)
        self.pin_btn.setMinimumHeight(36)
        self.pin_btn.clicked.connect(self.on_pin_toggle)
        actions_layout.addWidget(self.pin_btn)
        
        actions_layout.addStretch()
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setMinimumWidth(100)
        edit_btn.setMinimumHeight(36)
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setMinimumWidth(100)
        delete_btn.setMinimumHeight(36)
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self.reject)
        actions_layout.addWidget(close_btn)
        
        self.layout.addLayout(actions_layout)
    
    def on_pin_toggle(self):
        """Handle pin toggle"""
        self.pin_toggled.emit(self.note.id)
        self.note.pinned = not self.note.pinned
        pin_text = "📍 Unpin" if self.note.pinned else "📌 Pin"
        self.pin_btn.setText(pin_text)
    
    def on_edit(self):
        """Handle edit button"""
        self.edit_requested.emit(self.note.id)
        self.accept()
    
    def on_delete(self):
        """Handle delete button"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Note",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.note.id)
            self.accept()
