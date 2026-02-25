"""
Note Dialog
Dialog for creating/editing notes
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QCheckBox, QSizePolicy, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from src.shared.dialogs import BaseDialog


class NoteDialog(BaseDialog):
    """Dialog for creating/editing notes"""
    
    def __init__(self, parent=None, note=None):
        self.note = note
        self.is_edit = note is not None
        
        title = "Edit Note" if self.is_edit else "New Note"
        super().__init__(parent, title, width=600, height=500)
        self.setup_content()
        self.add_buttons(save_text="Save Note", on_save=self.on_save)
    
    def setup_content(self):
        """Setup dialog content"""
        # Title
        title_label = QLabel("Title:")
        self.layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter note title...")
        if self.note:
            self.title_input.setText(self.note.title)
        self.layout.addWidget(self.title_input)
        
        # Content with styled text editor and resize grip
        content_label = QLabel("Content:")
        self.layout.addWidget(content_label)
        
        # Create content input with proper styling
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your note here...")
        self.content_input.setMinimumHeight(200)
        self.content_input.setMaximumHeight(400)
        self.content_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        if self.note:
            self.content_input.setPlainText(self.note.content)
        
        # Apply theme styling
        self._apply_content_styling()
        
        # Add resize handle
        content_container = QVBoxLayout()
        content_container.setSpacing(0)
        content_container.addWidget(self.content_input)
        
        # Resize grip
        resize_handle = QLabel()
        try:
            pixmap = QPixmap("assets/icons/resize-grip.svg")
            resize_handle.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                                  Qt.TransformationMode.SmoothTransformation))
        except:
            resize_handle.setText("⋮⋮")
        
        resize_handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        resize_handle.setFixedHeight(20)
        resize_handle.setStyleSheet("padding-right: 5px; padding-bottom: 2px;")
        resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        
        resize_handle.mousePressEvent = lambda e: self._start_resize(e)
        resize_handle.mouseMoveEvent = lambda e: self._do_resize(e, 200, 400)
        
        content_container.addWidget(resize_handle)
        
        self.layout.addLayout(content_container)
        
        # Tags
        tags_label = QLabel("Tags (comma-separated):")
        self.layout.addWidget(tags_label)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g., work, ideas, personal")
        if self.note:
            self.tags_input.setText(self.note.tags or "")
        self.layout.addWidget(self.tags_input)
        
        # Pinned checkbox
        self.pinned_check = QCheckBox("📌 Pin this note to the top")
        if self.note:
            self.pinned_check.setChecked(self.note.pinned)
        self.layout.addWidget(self.pinned_check)
    
    def _apply_content_styling(self):
        """Apply theme styling to content field"""
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.content_input.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 10pt;
                    }}
                    QTextEdit::corner {{
                        background-color: {theme_obj.bg_tertiary};
                        border: 1px solid {theme_obj.border};
                    }}
                """)
                db.close()
            except:
                pass
    
    def _start_resize(self, event):
        """Start resizing content box"""
        self.resize_start_y = event.globalPosition().y()
        self.resize_start_height = self.content_input.height()
    
    def _do_resize(self, event, min_height, max_height):
        """Resize content box"""
        if hasattr(self, 'resize_start_y'):
            delta = event.globalPosition().y() - self.resize_start_y
            new_height = max(min_height, min(max_height, self.resize_start_height + delta))
            self.content_input.setFixedHeight(int(new_height))
    
    def get_data(self):
        """Get note data from dialog"""
        return {
            'title': self.title_input.text().strip(),
            'content': self.content_input.toPlainText().strip(),
            'tags': self.tags_input.text().strip(),
            'pinned': self.pinned_check.isChecked()
        }
    
    def validate(self):
        """Validate note data"""
        data = self.get_data()
        
        if not data['title']:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Title is required")
            return False
        
        if not data['content']:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Content is required")
            return False
        
        return True
    
    def on_save(self):
        """Handle save button click"""
        if self.validate():
            self.accept()

