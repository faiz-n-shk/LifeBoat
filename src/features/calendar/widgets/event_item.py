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
        self.setObjectName("event-item-card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Set maximum width to fit within parent container
        self.setMaximumWidth(320)
        
        # Set size policy
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet("""
            QFrame#event-item-card {
                background: rgba(60, 60, 80, 0.3);
                border: 1px solid rgba(80, 80, 100, 0.3);
                border-radius: 8px;
                max-width: 320px;
            }
            QFrame#event-item-card:hover {
                background: rgba(70, 70, 90, 0.4);
                border-color: rgba(100, 150, 255, 0.4);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSizeConstraint(layout.SizeConstraint.SetMinAndMaxSize)
        
        # Title with color indicator
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        # Color indicator
        color_box = QFrame()
        color_box.setFixedSize(4, 20)
        color_box.setStyleSheet(f"background-color: {self.event.color}; border-radius: 2px;")
        title_layout.addWidget(color_box)
        
        # Title
        from PyQt6.QtWidgets import QSizePolicy
        title_label = QLabel(self.event.title)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_label.setMaximumWidth(270)
        title_layout.addWidget(title_label, 1)
        
        layout.addLayout(title_layout)
        
        # Date/Time
        date_str = self.event.start_date.strftime("%a, %b %d, %Y")
        if not self.event.all_day:
            time_str = self.event.start_date.strftime("%I:%M %p")
            date_str += f" at {time_str}"
        
        date_label = QLabel(date_str)
        date_label.setWordWrap(True)
        date_label.setMaximumWidth(290)
        date_label.setStyleSheet("font-size: 9pt; color: rgba(255, 255, 255, 0.6);")
        layout.addWidget(date_label)
        
        # Location
        if self.event.location:
            loc_label = QLabel(f"📍 {self.event.location}")
            loc_label.setWordWrap(True)
            loc_label.setMaximumWidth(290)
            loc_label.setStyleSheet("font-size: 9pt; color: rgba(255, 255, 255, 0.6);")
            layout.addWidget(loc_label)
        
        # Description
        if self.event.description:
            desc_label = QLabel(self.truncate_text(self.event.description, 80))
            desc_label.setWordWrap(True)
            desc_label.setMaximumWidth(290)
            desc_label.setStyleSheet("font-size: 8pt; color: rgba(255, 255, 255, 0.5);")
            layout.addWidget(desc_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(6)
        actions_layout.addStretch()
        
        from PyQt6.QtGui import QIcon
        from src.core.path_manager import get_resource_path
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(get_resource_path("assets/icons/edit.svg")))
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("QPushButton { border-radius: 14px; padding: 0px; }")
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path("assets/icons/delete.svg")))
        delete_btn.setFixedSize(28, 28)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setProperty("class", "danger-button")
        delete_btn.setStyleSheet("QPushButton { border-radius: 14px; padding: 0px; }")
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)
    
    def mousePressEvent(self, event):
        """Handle click on event item - navigate to date"""
        # Get the calendar view parent
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to_date'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'navigate_to_date'):
            parent.navigate_to_date(self.event.start_date.date())
        
        super().mousePressEvent(event)
    
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
