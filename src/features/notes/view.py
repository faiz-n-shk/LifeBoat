"""
Notes View
Notes management interface with multiple view modes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from src.shared.dialogs import NoScrollComboBox
from src.core.path_manager import get_resource_path
from src.shared.icon_utils import load_accent_icon, load_themed_icon
from src.shared.search_bar import SearchBar

from src.features.notes.controller import NotesController
from src.features.notes.widgets.note_dialog import NoteDialog
from src.features.notes.widgets.note_viewer import NoteViewer
from src.features.notes.widgets.note_card import NoteCard
from src.shared.flow_layout import FlowLayout


class NotesView(QWidget):
    """Notes management view with responsive layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = NotesController()
        
        # Load saved view mode and filter state
        from src.core.config import config
        self.current_view_mode = config.get('notes.view_mode', 'Grid')
        self.saved_tag_filter = config.get('notes.tag_filter', 'All Tags')
        self.saved_pinned_filter = config.get('notes.pinned_filter', False)
        
        self.setup_ui()
        self.update_tag_filter()  # Load tags on initialization
        self.restore_filter_state()
        self.load_notes()
    
    def setup_ui(self):
        """Setup notes UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.header_icon_label = QLabel()
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/icon_notes.svg"), size=(24, 24))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)
        header_layout.addWidget(self.header_icon_label)
        
        title = QLabel("Notes")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # View mode selector
        view_label = QLabel("View:")
        header_layout.addWidget(view_label)
        
        self.view_mode_combo = NoScrollComboBox()
        self.view_mode_combo.addItems(["Auto", "Grid", "List", "Compact"])
        self.view_mode_combo.setCurrentText(self.current_view_mode)
        self.view_mode_combo.setMinimumWidth(100)
        self.view_mode_combo.currentTextChanged.connect(self.on_view_mode_changed)
        header_layout.addWidget(self.view_mode_combo)
        
        # New note button with icon
        new_btn = QPushButton(" New Note")
        new_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_plus.svg")))
        new_btn.setIconSize(QSize(16, 16))
        new_btn.setMinimumWidth(120)
        new_btn.setMinimumHeight(36)
        new_btn.clicked.connect(self.on_new_note)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filters
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        from src.shared.search_bar import SearchBar
        
        self.search_input = SearchBar("Search notes...")
        self.search_input.textChanged.connect(self.on_search)
        controls_layout.addWidget(self.search_input, 3)
        
        # Tag filter
        self.tag_filter = NoScrollComboBox()
        self.tag_filter.setMinimumHeight(36)
        self.tag_filter.setMinimumWidth(150)
        self.tag_filter.addItem("All Tags")
        self.tag_filter.currentTextChanged.connect(self.on_filter_changed)
        controls_layout.addWidget(self.tag_filter, 1)
        
        # Pinned toggle
        self.pinned_btn = QPushButton()
        self.pinned_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_pin.svg")))
        self.pinned_btn.setIconSize(QSize(16, 16))
        self.pinned_btn.setText(" Pinned")
        self.pinned_btn.setCheckable(True)
        self.pinned_btn.setMinimumHeight(36)
        self.pinned_btn.setMinimumWidth(100)
        self.pinned_btn.clicked.connect(self.on_filter_changed)
        controls_layout.addWidget(self.pinned_btn)
        
        # Apply initial styling
        self.update_pinned_button_style()
        
        layout.addLayout(controls_layout)
        
        # Scroll area for notes
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container for notes
        self.notes_container = QWidget()
        self.notes_layout = FlowLayout(self.notes_container)
        self.notes_layout.setSpacing(15)
        
        self.scroll.setWidget(self.notes_container)
        
        # Empty state overlay (hidden by default)
        self.empty_overlay = QWidget(self.scroll)
        self.empty_overlay.setStyleSheet("background: transparent;")
        empty_layout = QVBoxLayout(self.empty_overlay)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # SVG icon with proper rendering
        empty_icon = QLabel()
        icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_notes.svg"), size=(80, 80))
        empty_icon.setPixmap(icon_pixmap)
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_label = QLabel("No notes yet")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        empty_label.setFont(font)
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_label)
        
        empty_hint = QLabel("Click '+ New Note' to create your first note")
        empty_hint.setProperty("class", "secondary-text")
        font = QFont()
        font.setPointSize(12)
        empty_hint.setFont(font)
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_hint)
        
        self.empty_overlay.hide()
        
        layout.addWidget(self.scroll)
        
        self.setLayout(layout)
    
    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'empty_overlay') and self.empty_overlay.isVisible():
            self.empty_overlay.setGeometry(self.scroll.viewport().rect())
    
    def load_notes(self):
        # Clear existing notes
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get filter criteria
        search_query = self.search_input.text().strip()
        pinned_only = self.pinned_btn.isChecked()
        
        # Get notes
        notes = self.controller.get_all_notes(search_query, pinned_only)
        
        # Filter by tag if selected
        selected_tag = self.tag_filter.currentText()
        if selected_tag == "No Tags":
            notes = [n for n in notes if not n.tags or not n.tags.strip()]
        elif selected_tag != "All Tags":
            notes = [n for n in notes if n.tags and selected_tag in [t.strip() for t in n.tags.split(',')]]
        
        # Show/hide empty overlay
        if notes:
            self.empty_overlay.hide()
            for note in notes:
                note_card = NoteCard(note, view_mode=self.current_view_mode)
                note_card.clicked.connect(self.create_edit_handler(note.id))
                note_card.pin_clicked.connect(self.on_toggle_pin)
                note_card.delete_clicked.connect(self.on_delete_note)
                self.notes_layout.addWidget(note_card)
        else:
            self.empty_overlay.setGeometry(self.scroll.viewport().rect())
            self.empty_overlay.show()
            self.empty_overlay.raise_()
    
    def create_edit_handler(self, note_id):
        """Create a handler function for viewing a specific note"""
        def handler():
            self.on_view_note(note_id)
        return handler
    
    def on_view_note(self, note_id: int):
        """Handle viewing a note"""
        note = self.controller.get_note_by_id(note_id)
        if note:
            viewer = NoteViewer(self, note, self.controller)
            viewer.edit_requested.connect(self.on_edit_note)
            viewer.delete_requested.connect(self.on_delete_note)
            viewer.pin_toggled.connect(self.on_toggle_pin)
            viewer.exec()
            # Refresh after viewer closes
            self.load_notes()
    
    def on_view_mode_changed(self, mode):
        """Handle view mode change"""
        self.current_view_mode = mode
        
        # Save view mode to config
        from src.core.config import config
        config.set('notes.view_mode', mode)
        config.save()
        
        self.load_notes()
    
    def restore_filter_state(self):
        """Restore saved filter state"""
        # Restore pinned filter
        self.pinned_btn.setChecked(self.saved_pinned_filter)
    
    def save_filter_state(self):
        """Save current filter state"""
        from src.core.config import config
        config.set('notes.tag_filter', self.tag_filter.currentText())
        config.set('notes.pinned_filter', self.pinned_btn.isChecked())
        config.save()
    
    def update_tag_filter(self):
        """Update the tag filter dropdown with available tags"""
        self.tag_filter.blockSignals(True)
        
        current_tag = self.tag_filter.currentText()
        # Use saved tag filter if current is default
        if current_tag == "All Tags" and hasattr(self, 'saved_tag_filter'):
            current_tag = self.saved_tag_filter
        
        self.tag_filter.clear()
        self.tag_filter.addItem("All Tags")
        self.tag_filter.addItem("No Tags")
        
        tags = self.controller.get_all_tags()
        for tag in tags:
            self.tag_filter.addItem(tag)
        
        index = self.tag_filter.findText(current_tag)
        if index >= 0:
            self.tag_filter.setCurrentIndex(index)
        
        self.tag_filter.blockSignals(False)
    
    def on_new_note(self):
        """Handle new note button click"""
        dialog = NoteDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            note = self.controller.create_note(
                title=data['title'],
                content=data['content'],
                tags=data['tags'],
                pinned=data['pinned']
            )
            if note:
                self.update_tag_filter()
                self.load_notes()
    
    def on_edit_note(self, note_id: int):
        """Handle edit note"""
        note = self.controller.get_note_by_id(note_id)
        if note:
            dialog = NoteDialog(self, note)
            if dialog.exec():
                data = dialog.get_data()
                if self.controller.update_note(
                    note_id=note_id,
                    title=data['title'],
                    content=data['content'],
                    tags=data['tags'],
                    pinned=data['pinned']
                ):
                    self.update_tag_filter()
                    self.load_notes()
    
    def on_delete_note(self, note_id: int):
        """Handle delete note"""
        from src.shared.dialogs import create_message_box
        
        msg = create_message_box(
            self,
            "Delete Note",
            "Are you sure you want to delete this note?",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg == QMessageBox.StandardButton.Yes:
            if self.controller.delete_note(note_id):
                self.update_tag_filter()
                self.load_notes()
    
    def on_toggle_pin(self, note_id: int):
        """Handle toggle pin"""
        if self.controller.toggle_pin(note_id):
            self.load_notes()
    
    def on_search(self):
        """Handle search text change"""
        self.load_notes()
    
    def on_filter_changed(self):
        """Handle filter change"""
        self.save_filter_state()
        self.load_notes()
    
    def refresh(self):
        """Refresh view"""
        # Reload header icon with current theme
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/feature_notes.svg"), size=(24, 24))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)
        
        self.update_tag_filter()
        self.update_pinned_button_style()
        self.load_notes()
    
    def resizeEvent(self, event):
        """Handle resize to keep overlay sized correctly"""
        super().resizeEvent(event)
        if hasattr(self, 'empty_overlay') and self.empty_overlay.isVisible():
            self.empty_overlay.setGeometry(self.scroll.rect())
    
    def update_pinned_button_style(self):
        """Update pinned button styling based on current theme"""
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            self.pinned_btn.setStyleSheet(f"""
                QPushButton:checked {{
                    background-color: {theme_obj.success};
                    color: {theme_obj.bg_primary};
                    font-weight: bold;
                }}
            """)
            db.close()
        except:
            pass
