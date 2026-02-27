"""
Note Card Widget
Individual note card with multiple view modes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor, QIcon

from src.shared.formatters import format_datetime


class NoteCard(QFrame):
    """Note card with support for different view modes"""
    
    clicked = pyqtSignal(int)
    pin_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    
    def __init__(self, note, view_mode="Auto", parent=None):
        super().__init__(parent)
        self.note = note
        self.view_mode = view_mode
        self.setup_ui()
    
    def setup_ui(self):
        """Setup note card UI based on view mode"""
        self.setObjectName("note-card")
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Base stylesheet for all cards
        self.setStyleSheet("""
            QFrame#note-card {
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 8px;
                background-color: rgba(50, 50, 50, 0.2);
                padding: 0px;
            }
            QFrame#note-card:hover {
                border-color: rgba(100, 150, 255, 0.5);
                background-color: rgba(50, 50, 50, 0.3);
            }
            QPushButton {
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 4px;
                background-color: rgba(80, 80, 80, 0.3);
                min-width: 2em;
                min-height: 2em;
                padding: 0.3em;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 0.5);
                border-color: rgba(100, 150, 255, 0.5);
            }
        """)
        
        if self.view_mode == "Auto":
            self.setup_auto_view()
        elif self.view_mode == "Grid":
            self.setup_grid_view()
        elif self.view_mode == "List":
            self.setup_list_view()
        else:
            self.setup_compact_view()
    
    def setup_auto_view(self):
        """Setup auto view (responsive card style)"""
        # Use size policies for dynamic sizing
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        self.setMinimumHeight(180)
        self.setMaximumHeight(450)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # Title with pin
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
        
        title = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        title_layout.addWidget(title, 1)
        
        if self.note.pinned:
            pin_icon = QLabel("📌")
            font = QFont()
            font.setPointSize(14)
            pin_icon.setFont(font)
            pin_icon.setFixedSize(24, 24)
            pin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(pin_icon)
        
        main_layout.addLayout(title_layout)
        
        # Content box
        content_container = QFrame()
        content_container.setObjectName("note-content-box")
        content_container.setFrameShape(QFrame.Shape.StyledPanel)
        content_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_container.setStyleSheet("""
            QFrame#note-content-box {
                background-color: rgba(100, 100, 100, 0.1);
                border: 1px solid rgba(100, 100, 100, 0.2);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        content_preview = self.note.content[:300]
        if len(self.note.content) > 300:
            content_preview += "..."
        
        content_label = QLabel(content_preview)
        content_label.setWordWrap(True)
        content_label.setProperty("class", "secondary-text")
        content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        font = QFont()
        font.setPointSize(9)
        content_label.setFont(font)
        content_layout.addWidget(content_label)
        
        main_layout.addWidget(content_container, 1)
        
        # Tags
        if self.note.tags and self.note.tags.strip():
            self.add_tags(main_layout)
        else:
            # Show "no tags" indicator
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)
            
            no_tag_pill = QLabel("no tags")
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            no_tag_pill.setFont(font)
            no_tag_pill.setStyleSheet("""
                QLabel {
                    padding: 0.3em 0.8em;
                    border-radius: 10px;
                    background-color: rgba(100, 100, 100, 0.15);
                    border: 1px solid rgba(100, 100, 100, 0.25);
                    color: rgba(150, 150, 150, 0.8);
                }
            """)
            tags_layout.addWidget(no_tag_pill)
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
        
        # Footer
        self.add_footer(main_layout)
        
        self.setLayout(main_layout)
    
    def setup_grid_view(self):
        """Setup grid view (fixed card style)"""
        self.setFixedWidth(300)
        self.setMinimumHeight(200)
        self.setMaximumHeight(400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # Title with pin
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
        
        title = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        title_layout.addWidget(title, 1)
        
        if self.note.pinned:
            pin_icon = QLabel("📌")
            font = QFont()
            font.setPointSize(14)
            pin_icon.setFont(font)
            pin_icon.setFixedSize(24, 24)
            pin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(pin_icon)
        
        main_layout.addLayout(title_layout)
        
        # Content box
        content_container = QFrame()
        content_container.setObjectName("note-content-box")
        content_container.setFrameShape(QFrame.Shape.StyledPanel)
        content_container.setStyleSheet("""
            QFrame#note-content-box {
                background-color: rgba(100, 100, 100, 0.1);
                border: 1px solid rgba(100, 100, 100, 0.2);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        content_preview = self.note.content[:300]
        if len(self.note.content) > 300:
            content_preview += "..."
        
        content_label = QLabel(content_preview)
        content_label.setWordWrap(True)
        content_label.setProperty("class", "secondary-text")
        font = QFont()
        font.setPointSize(9)
        content_label.setFont(font)
        content_layout.addWidget(content_label)
        
        main_layout.addWidget(content_container, 1)
        
        # Tags
        if self.note.tags and self.note.tags.strip():
            self.add_tags(main_layout)
        else:
            # Show "no tags" indicator
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)
            
            no_tag_pill = QLabel("no tags")
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            no_tag_pill.setFont(font)
            no_tag_pill.setStyleSheet("""
                QLabel {
                    padding: 0.3em 0.8em;
                    border-radius: 10px;
                    background-color: rgba(100, 100, 100, 0.15);
                    border: 1px solid rgba(100, 100, 100, 0.25);
                    color: rgba(150, 150, 150, 0.8);
                }
            """)
            tags_layout.addWidget(no_tag_pill)
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
        
        # Footer
        self.add_footer(main_layout)
        
        self.setLayout(main_layout)
    
    def setup_list_view(self):
        """Setup list view (horizontal layout)"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(400)
        self.setMaximumWidth(600)
        self.setFixedHeight(100)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(16)
        
        # Left side: Title, tags, and date in vertical layout
        left_layout = QVBoxLayout()
        left_layout.setSpacing(6)
        
        # Title with pin
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(False)
        title_layout.addWidget(title)
        
        if self.note.pinned:
            pin_icon = QLabel("📌")
            font = QFont()
            font.setPointSize(14)
            pin_icon.setFont(font)
            pin_icon.setFixedSize(24, 24)
            pin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(pin_icon)
        
        title_layout.addStretch()
        left_layout.addLayout(title_layout)
        
        # Tags in the middle
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(6)
        
        if self.note.tags and self.note.tags.strip():
            for tag in self.note.tags.split(',')[:4]:
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
                            border-radius: 11px;
                            background-color: rgba(100, 150, 255, 0.2);
                            border: 1px solid rgba(100, 150, 255, 0.4);
                        }
                    """)
                    tags_layout.addWidget(tag_pill)
        else:
            # Show "no tags" indicator
            no_tag_pill = QLabel("no tags")
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            no_tag_pill.setFont(font)
            no_tag_pill.setStyleSheet("""
                QLabel {
                    padding: 0.3em 0.8em;
                    border-radius: 11px;
                    background-color: rgba(100, 100, 100, 0.15);
                    border: 1px solid rgba(100, 100, 100, 0.25);
                    color: rgba(150, 150, 150, 0.8);
                }
            """)
            tags_layout.addWidget(no_tag_pill)
        
        tags_layout.addStretch()
        left_layout.addLayout(tags_layout)
        
        # Date at the bottom
        date_label = QLabel(format_datetime(self.note.updated_at))
        date_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        date_label.setFont(font)
        left_layout.addWidget(date_label)
        
        main_layout.addLayout(left_layout, 1)
        
        # Right side: Actions only
        right_layout = QVBoxLayout()
        right_layout.addStretch()
        
        actions_layout = QHBoxLayout()
        self.add_action_buttons(actions_layout, size=28)
        right_layout.addLayout(actions_layout)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout)
        
        self.setLayout(main_layout)
    
    def setup_compact_view(self):
        """Setup compact view (minimal)"""
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedWidth(200)
        self.setFixedHeight(60)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)
        
        # Title with pin
        title_layout = QHBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(False)
        title_layout.addWidget(title, 1)
        
        if self.note.pinned:
            pin_icon = QLabel("📌")
            font = QFont()
            font.setPointSize(12)
            pin_icon.setFont(font)
            pin_icon.setFixedSize(20, 20)
            pin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(pin_icon)
        
        main_layout.addLayout(title_layout)
        
        main_layout.addStretch()
        
        # Footer with date only (no action buttons)
        footer_layout = QHBoxLayout()
        date_label = QLabel(format_datetime(self.note.updated_at))
        date_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(7)
        date_label.setFont(font)
        footer_layout.addWidget(date_label)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)
    
    def add_tags(self, layout):
        """Add tags to layout"""
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(4)
        
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
        layout.addLayout(tags_layout)
    
    def add_footer(self, layout):
        """Add footer to layout"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)
        
        date_label = QLabel(format_datetime(self.note.updated_at))
        date_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(8)
        date_label.setFont(font)
        footer_layout.addWidget(date_label)
        
        footer_layout.addStretch()
        self.add_action_buttons(footer_layout)
        layout.addLayout(footer_layout)
    
    def add_action_buttons(self, layout, size=32):
        """Add action buttons to layout"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(6)
        
        # Pin button
        from src.core.path_manager import get_resource_path
        
        pin_btn = QPushButton()
        pin_btn.setFixedSize(size, size)
        pin_btn.setToolTip("Pin" if not self.note.pinned else "Unpin")
        pin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        try:
            pin_icon = QIcon(get_resource_path("assets/icons/check.svg"))
            pin_btn.setIcon(pin_icon)
            pin_btn.setIconSize(QSize(int(size * 0.6), int(size * 0.6)))
        except:
            pin_label = QLabel("📌" if not self.note.pinned else "📍")
            font = QFont()
            font.setPointSize(int(size * 0.4))
            pin_label.setFont(font)
            pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pin_btn.setText("")
            pin_btn_layout = QVBoxLayout(pin_btn)
            pin_btn_layout.setContentsMargins(0, 0, 0, 0)
            pin_btn_layout.addWidget(pin_label)
        
        pin_btn.clicked.connect(lambda: self.pin_clicked.emit(self.note.id))
        actions_layout.addWidget(pin_btn)
        
        # Edit button
        edit_btn = QPushButton()
        edit_btn.setFixedSize(size, size)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        try:
            edit_icon = QIcon(get_resource_path("assets/icons/edit.svg"))
            edit_btn.setIcon(edit_icon)
            edit_btn.setIconSize(QSize(int(size * 0.6), int(size * 0.6)))
        except:
            edit_label = QLabel("✏️")
            font = QFont()
            font.setPointSize(int(size * 0.4))
            edit_label.setFont(font)
            edit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            edit_btn.setText("")
            edit_btn_layout = QVBoxLayout(edit_btn)
            edit_btn_layout.setContentsMargins(0, 0, 0, 0)
            edit_btn_layout.addWidget(edit_label)
        
        edit_btn.clicked.connect(lambda: self.clicked.emit(self.note.id))
        actions_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setFixedSize(size, size)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        try:
            delete_icon = QIcon(get_resource_path("assets/icons/delete.svg"))
            delete_btn.setIcon(delete_icon)
            delete_btn.setIconSize(QSize(int(size * 0.6), int(size * 0.6)))
        except:
            delete_label = QLabel("🗑️")
            font = QFont()
            font.setPointSize(int(size * 0.4))
            delete_label.setFont(font)
            delete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            delete_btn.setText("")
            delete_btn_layout = QVBoxLayout(delete_btn)
            delete_btn_layout.setContentsMargins(0, 0, 0, 0)
            delete_btn_layout.addWidget(delete_label)
        
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.note.id))
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)
    
    def mousePressEvent(self, event):
        """Handle mouse press to open note viewer"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # Check if click is on action buttons area
                if not self._is_click_on_buttons(event.position()):
                    self.clicked.emit(self.note.id)
            super().mousePressEvent(event)
        except RuntimeError:
            # Widget has been deleted, ignore the event
            pass
    
    def _is_click_on_buttons(self, pos):
        """Check if click position is on action buttons"""
        # Get the geometry of the card
        card_rect = self.rect()
        # Buttons are typically in the bottom-right corner
        # Reserve bottom 40px and right 120px for buttons
        button_area = card_rect.adjusted(card_rect.width() - 120, card_rect.height() - 40, 0, 0)
        return button_area.contains(pos.toPoint())
