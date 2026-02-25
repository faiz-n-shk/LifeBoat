"""
Shared Custom Widgets
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator

from src.core.config import config


class TimePicker(QWidget):
    """
    Custom time picker widget with hour and minute selectors
    Adapts to 12hr/24hr mode based on config
    """
    
    time_changed = pyqtSignal(int, int)  # hour, minute in 24hr format
    
    def __init__(self, parent=None, hour=9, minute=0):
        super().__init__(parent)
        self.hour_24 = hour
        self.minute = minute
        
        # Get time mode from config
        self.time_mode = config.get('datetime.time_mode', '12hr')
        
        # Convert to 12hr if needed
        if self.time_mode == '12hr':
            self.am_pm = 'AM' if self.hour_24 < 12 else 'PM'
            if self.hour_24 == 0:
                self.display_hour = 12
            elif self.hour_24 > 12:
                self.display_hour = self.hour_24 - 12
            else:
                self.display_hour = self.hour_24
        else:
            self.display_hour = self.hour_24
            self.am_pm = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup time picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Reduced from 10 to 5
        
        # Hour selector
        hour_container = self.create_selector(
            "Hour",
            self.display_hour,
            self.hour_up,
            self.hour_down,
            self.validate_hour
        )
        self.hour_entry = hour_container.findChild(QLineEdit)
        layout.addWidget(hour_container)
        
        # Separator
        sep = QLabel(":")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        sep.setFont(font)
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sep)
        
        # Minute selector
        minute_container = self.create_selector(
            "Minute",
            self.minute,
            self.minute_up,
            self.minute_down,
            self.validate_minute
        )
        self.minute_entry = minute_container.findChild(QLineEdit)
        layout.addWidget(minute_container)
        
        # AM/PM selector for 12hr mode
        if self.time_mode == '12hr':
            ampm_container = self.create_ampm_selector()
            layout.addWidget(ampm_container)
        
        self.setLayout(layout)
    
    def create_selector(self, label_text, initial_value, up_callback, down_callback, validate_callback):
        """Create a time component selector (hour or minute)"""
        container = QFrame()
        container.setObjectName("time-selector")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        label = QLabel(label_text)
        label.setProperty("class", "small-text")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Up button
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(50, 25)
        up_btn.clicked.connect(up_callback)
        layout.addWidget(up_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Value entry
        entry = QLineEdit()
        entry.setText(f"{initial_value:02d}")
        entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry.setFixedSize(50, 30)
        entry.setValidator(QIntValidator(0, 99))
        entry.editingFinished.connect(validate_callback)
        layout.addWidget(entry, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Down button
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(50, 25)
        down_btn.clicked.connect(down_callback)
        layout.addWidget(down_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return container
    
    def create_ampm_selector(self):
        """Create AM/PM selector for 12hr mode"""
        container = QFrame()
        container.setObjectName("time-selector")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        label = QLabel("Period")
        label.setProperty("class", "small-text")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Up button (cycles AM/PM)
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(50, 25)
        up_btn.clicked.connect(self.toggle_ampm)
        layout.addWidget(up_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # AM/PM display button (also toggles on click)
        self.ampm_btn = QPushButton(self.am_pm)
        self.ampm_btn.setFixedSize(50, 30)
        self.ampm_btn.clicked.connect(self.toggle_ampm)
        layout.addWidget(self.ampm_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Down button (cycles AM/PM)
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(50, 25)
        down_btn.clicked.connect(self.toggle_ampm)
        layout.addWidget(down_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return container
    
    def hour_up(self):
        """Increment hour by 1"""
        if self.time_mode == '12hr':
            self.display_hour = (self.display_hour % 12) + 1
        else:
            self.display_hour = (self.display_hour + 1) % 24
        self.hour_entry.setText(f"{self.display_hour:02d}")
        self.emit_time_changed()
    
    def hour_down(self):
        """Decrement hour by 1"""
        if self.time_mode == '12hr':
            self.display_hour = self.display_hour - 1 if self.display_hour > 1 else 12
        else:
            self.display_hour = (self.display_hour - 1) % 24
        self.hour_entry.setText(f"{self.display_hour:02d}")
        self.emit_time_changed()
    
    def minute_up(self):
        """Increment minute by 5"""
        self.minute = (self.minute + 5) % 60
        self.minute_entry.setText(f"{self.minute:02d}")
        self.emit_time_changed()
    
    def minute_down(self):
        """Decrement minute by 5"""
        self.minute = (self.minute - 5) % 60
        self.minute_entry.setText(f"{self.minute:02d}")
        self.emit_time_changed()
    
    def validate_hour(self):
        """Validate and update hour from entry"""
        try:
            hour = int(self.hour_entry.text())
            if self.time_mode == '12hr':
                if 1 <= hour <= 12:
                    self.display_hour = hour
            else:
                if 0 <= hour <= 23:
                    self.display_hour = hour
            self.hour_entry.setText(f"{self.display_hour:02d}")
            self.emit_time_changed()
        except:
            self.hour_entry.setText(f"{self.display_hour:02d}")
    
    def validate_minute(self):
        """Validate and update minute from entry"""
        try:
            minute = int(self.minute_entry.text())
            if 0 <= minute <= 59:
                self.minute = minute
            self.minute_entry.setText(f"{self.minute:02d}")
            self.emit_time_changed()
        except:
            self.minute_entry.setText(f"{self.minute:02d}")
    
    def set_ampm(self, period):
        """Set AM/PM period"""
        if self.time_mode == '12hr':
            self.am_pm = period
            if hasattr(self, 'ampm_btn'):
                self.ampm_btn.setText(self.am_pm)
            self.emit_time_changed()
    
    def toggle_ampm(self):
        """Toggle between AM and PM"""
        if self.time_mode == '12hr':
            self.am_pm = 'PM' if self.am_pm == 'AM' else 'AM'
            if hasattr(self, 'ampm_btn'):
                self.ampm_btn.setText(self.am_pm)
            self.emit_time_changed()
    
    def emit_time_changed(self):
        """Emit time changed signal with 24hr format"""
        hour_24, minute = self.get_time()
        self.time_changed.emit(hour_24, minute)
    
    def get_time(self):
        """
        Get selected time in 24-hour format
        
        Returns:
            tuple: (hour, minute) as integers in 24-hour format
        """
        if self.time_mode == '12hr':
            # Convert 12hr to 24hr
            hour_24 = self.display_hour
            if self.am_pm == 'PM' and hour_24 != 12:
                hour_24 += 12
            elif self.am_pm == 'AM' and hour_24 == 12:
                hour_24 = 0
            return (hour_24, self.minute)
        else:
            return (self.display_hour, self.minute)
    
    def set_time(self, hour, minute):
        """
        Set time (in 24-hour format)
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        self.hour_24 = hour
        self.minute = minute
        
        if self.time_mode == '12hr':
            self.am_pm = 'AM' if hour < 12 else 'PM'
            if hour == 0:
                self.display_hour = 12
            elif hour > 12:
                self.display_hour = hour - 12
            else:
                self.display_hour = hour
            
            if hasattr(self, 'ampm_btn'):
                self.ampm_btn.setText(self.am_pm)
        else:
            self.display_hour = hour
        
        if hasattr(self, 'hour_entry'):
            self.hour_entry.setText(f"{self.display_hour:02d}")
            self.minute_entry.setText(f"{self.minute:02d}")
