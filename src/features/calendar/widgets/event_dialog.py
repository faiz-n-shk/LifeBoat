"""
Event Dialog
Dialog for creating/editing calendar events
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QDateEdit,
    QTimeEdit, QCheckBox, QSpinBox, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont
from datetime import datetime

from src.models.event import Event
from src.core.config import config


class EventDialog(QDialog):
    """Dialog for creating/editing events"""
    
    def __init__(self, parent=None, event: Event = None):
        super().__init__(parent)
        self.event = event
        self.setup_ui()
        
        if event:
            self.load_event_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Edit Event" if self.event else "Add Event")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Edit Event" if self.event else "Add Event")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Title field
        title_label = QLabel("Title:")
        form_layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Event title")
        form_layout.addWidget(self.title_input)
        
        # Date and time
        datetime_layout = QHBoxLayout()
        datetime_layout.setSpacing(10)
        
        # Start date
        date_layout = QVBoxLayout()
        date_layout.setSpacing(5)
        date_label = QLabel("Date:")
        date_layout.addWidget(date_label)
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.apply_locale_to_calendar()
        date_layout.addWidget(self.date_input)
        
        datetime_layout.addLayout(date_layout, 1)
        
        # Start time
        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        time_label = QLabel("Time:")
        time_layout.addWidget(time_label)
        
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        
        # Set display format based on config
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '12hr':
            self.time_input.setDisplayFormat("hh:mm AP")
        else:
            self.time_input.setDisplayFormat("HH:mm")
        
        time_layout.addWidget(self.time_input)
        
        datetime_layout.addLayout(time_layout)
        
        form_layout.addLayout(datetime_layout)
        
        # All day checkbox
        self.all_day_check = QCheckBox("All day event")
        self.all_day_check.stateChanged.connect(self.on_all_day_changed)
        form_layout.addWidget(self.all_day_check)
        
        # Location
        location_label = QLabel("Location:")
        form_layout.addWidget(location_label)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Event location (optional)")
        form_layout.addWidget(self.location_input)
        
        # Description
        desc_label = QLabel("Description:")
        form_layout.addWidget(desc_label)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Event description (optional)")
        self.description_input.setMinimumHeight(80)
        self.description_input.setMaximumHeight(150)
        # Set border explicitly
        from src.core.theme_manager import theme_manager
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        if theme:
            self.description_input.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {theme.bg_secondary};
                    color: {theme.fg_primary};
                    border: 2px solid {theme.border};
                    border-radius: 6px;
                    padding: 8px 12px;
                }}
            """)
        form_layout.addWidget(self.description_input)
        
        # Reminder
        reminder_label = QLabel("Reminder:")
        form_layout.addWidget(reminder_label)
        
        reminder_layout = QHBoxLayout()
        
        self.reminder_check = QCheckBox("Remind me")
        self.reminder_check.stateChanged.connect(self.on_reminder_changed)
        reminder_layout.addWidget(self.reminder_check)
        
        self.reminder_spin = QSpinBox()
        self.reminder_spin.setRange(5, 1440)
        self.reminder_spin.setValue(15)
        self.reminder_spin.setSuffix(" minutes before")
        self.reminder_spin.setEnabled(False)
        reminder_layout.addWidget(self.reminder_spin, 1)
        
        form_layout.addLayout(reminder_layout)
        
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.on_save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    def apply_locale_to_calendar(self):
        """Apply locale settings to calendar widget"""
        first_day = config.get('locale.week_starts_on', 'Monday')
        calendar_widget = self.date_input.calendarWidget()
        if calendar_widget:
            if first_day == "Sunday":
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
            else:
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
    
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
        self.date_input.setDate(QDate(
            self.event.start_date.year,
            self.event.start_date.month,
            self.event.start_date.day
        ))
        
        self.time_input.setTime(QTime(
            self.event.start_date.hour,
            self.event.start_date.minute
        ))
        
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
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please enter an event title.")
            return
        
        self.accept()
    
    def get_event_data(self) -> dict:
        """Get event data from form"""
        # Combine date and time
        date = self.date_input.date()
        time = self.time_input.time()
        
        start_date = datetime(
            date.year(),
            date.month(),
            date.day(),
            time.hour() if not self.all_day_check.isChecked() else 0,
            time.minute() if not self.all_day_check.isChecked() else 0
        )
        
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'start_date': start_date,
            'end_date': None,  # Could add end date field later
            'all_day': self.all_day_check.isChecked(),
            'location': self.location_input.text().strip() or None,
            'reminder_minutes': self.reminder_spin.value() if self.reminder_check.isChecked() else None,
            'color': self.event.color if self.event else '#0078d4'
        }
