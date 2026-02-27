"""
Event Dialog
Dialog for creating/editing calendar events
"""
from PyQt6.QtWidgets import QLabel, QLineEdit, QCheckBox, QSpinBox, QHBoxLayout
from PyQt6.QtCore import QDate, QTime
from src.shared.dialogs import NoScrollSpinBox

from src.models.event import Event
from src.core.config import config
from src.shared.dialogs import BaseDialog


class EventDialog(BaseDialog):
    """Dialog for creating/editing events"""
    
    def __init__(self, parent=None, event: Event = None):
        self.event = event
        self.is_edit = event is not None
        
        title = "Edit Event" if self.is_edit else "Add Event"
        super().__init__(parent, title=title, width=500, height=600)
        
        self.setup_fields()
        
        if self.is_edit:
            self.load_event_data()
    
    def setup_fields(self):
        """Setup event-specific fields"""
        # Title
        self.add_title_field(label="Title:", placeholder="Event title")
        
        # Date and time
        self.add_date_time_field(label="Date & Time:")
        
        # All day checkbox
        self.all_day_check = QCheckBox("All day event")
        self.all_day_check.stateChanged.connect(self.on_all_day_changed)
        self.layout.addWidget(self.all_day_check)
        
        # Location
        location_label = QLabel("Location:")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Event location (optional)")
        self.layout.addWidget(location_label)
        self.layout.addWidget(self.location_input)
        
        # Description
        self.add_description_field(label="Description:", placeholder="Event description (optional)")
        
        # Reminder
        reminder_label = QLabel("Reminder:")
        self.layout.addWidget(reminder_label)
        
        reminder_layout = QHBoxLayout()
        
        self.reminder_check = QCheckBox("Remind me")
        self.reminder_check.stateChanged.connect(self.on_reminder_changed)
        reminder_layout.addWidget(self.reminder_check)
        
        self.reminder_spin = NoScrollSpinBox()
        self.reminder_spin.setRange(5, 1440)
        self.reminder_spin.setValue(15)
        self.reminder_spin.setSuffix(" minutes before")
        self.reminder_spin.setEnabled(False)
        reminder_layout.addWidget(self.reminder_spin, 1)
        
        self.layout.addLayout(reminder_layout)
        
        # Buttons
        save_text = "Save" if self.is_edit else "Add Event"
        self.add_buttons(save_text=save_text, on_save=self.on_save)
    
    def on_all_day_changed(self, state):
        """Handle all day checkbox change"""
        self.time_input.setEnabled(state == 0)
    
    def on_reminder_changed(self, state):
        """Handle reminder checkbox change"""
        self.reminder_spin.setEnabled(state == 2)
    
    def load_event_data(self):
        """Load event data into form"""
        if not self.event:
            return
        
        self.title_input.setText(self.event.title)
        
        if self.event.description:
            self.description_input.setPlainText(self.event.description)
        
        # Date and time
        self.set_datetime(self.event.start_date)
        
        # All day
        self.all_day_check.setChecked(self.event.all_day)
        
        # Location
        if self.event.location:
            self.location_input.setText(self.event.location)
        
        # Reminder
        if self.event.reminder_minutes:
            self.reminder_check.setChecked(True)
            self.reminder_spin.setValue(self.event.reminder_minutes)
    
    def on_save(self):
        """Handle save button"""
        # Validate
        if not self.title_input.text().strip():
            from src.shared.dialogs import show_warning
            show_warning(self, "Validation Error", "Please enter an event title.")
            return
        
        self.accept()
    
    def get_event_data(self) -> dict:
        """Get event data from form"""
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'start_date': self.get_datetime(),
            'end_date': None,  # Could add end date field later
            'all_day': self.all_day_check.isChecked(),
            'location': self.location_input.text().strip() or None,
            'reminder_minutes': self.reminder_spin.value() if self.reminder_check.isChecked() else None,
            'color': self.event.color if self.event else '#0078d4'
        }
