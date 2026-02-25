"""
Event Item Widget
Individual event display in the events list
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.models.event import Event
from src.features.calendar.controller import CalendarController


class EventItem(QFrame):
    """Widget for displaying a single event"""
    
    event_updated = pyqtSignal()
    event_deleted = pyqtSignal()
    
    def __init__(self, event: Event, parent=None):
        super().__init__(parent)
        self.event = event
        self.controller = CalendarController()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup event item UI"""
        self.setObjectName("task-item")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Title with color indicator
        title_layout = QHBoxLayout()
        
        # Color indicator
        color_box = QFrame()
        color_box.setFixedSize(4, 20)
        color_box.setStyleSheet(f"background-color: {self.event.color}; border-radius: 2px;")
        title_layout.addWidget(color_box)
        
        # Title
        title_label = QLabel(self.event.title)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        title_label.setFont(font)
        title_layout.addWidget(title_label, 1)
        
        layout.addLayout(title_layout)
        
        # Date/Time
        date_str = self.event.start_date.strftime("%a, %b %d, %Y")
        if not self.event.all_day:
            time_str = self.event.start_date.strftime("%I:%M %p")
            date_str += f" at {time_str}"
        
        date_label = QLabel(date_str)
        date_label.setProperty("class", "meta-text")
        layout.addWidget(date_label)
        
        # Location
        if self.event.location:
            loc_label = QLabel(f"📍 {self.event.location}")
            loc_label.setProperty("class", "meta-text")
            layout.addWidget(loc_label)
        
        # Description
        if self.event.description:
            desc_label = QLabel(self.truncate_text(self.event.description, 100))
            desc_label.setProperty("class", "small-text")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger-button")
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
    
    def on_edit(self):
        """Handle edit button"""
        from src.features.calendar.widgets.event_dialog import EventDialog
        dialog = EventDialog(self, self.event)
        if dialog.exec():
            event_data = dialog.get_event_data()
            self.controller.update_event(self.event.id, event_data)
            self.event_updated.emit()
    
    def on_delete(self):
        """Handle delete button"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete event '{self.event.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_event(self.event.id)
            self.event_deleted.emit()
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
