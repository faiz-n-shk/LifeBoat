"""
Shared Dialog Components
Base classes and reusable components for all feature dialogs
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit,
    QPushButton, QScrollArea, QWidget, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QPixmap

from src.core.config import config


class BaseDialog(QDialog):
    """Base dialog with common functionality for all feature dialogs"""
    
    def __init__(self, parent=None, title="Dialog", width=450, height=550):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setFixedHeight(height)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)
        
        self.setLayout(self.main_layout)
    
    def add_title_field(self, label="Title:", placeholder="Enter title..."):
        """Add title input field"""
        title_label = QLabel(label)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(placeholder)
        self.layout.addWidget(title_label)
        self.layout.addWidget(self.title_input)
        return self.title_input
    
    def add_description_field(self, label="Description:", placeholder="Enter description (optional)...", 
                            min_height=60, max_height=200):
        """Add resizable description text field"""
        desc_label = QLabel(label)
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(min_height)
        self.description_input.setMaximumHeight(max_height)
        self.description_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.description_input.setPlaceholderText(placeholder)
        
        # Apply theme styling
        self._apply_description_styling()
        
        # Add resize handle
        desc_container = QVBoxLayout()
        desc_container.setSpacing(0)
        desc_container.addWidget(self.description_input)
        
        resize_handle = QLabel()
        from src.core.path_manager import get_resource_path
        pixmap = QPixmap(get_resource_path("assets/icons/resize-grip.svg"))
        resize_handle.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation))
        resize_handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        resize_handle.setFixedHeight(20)
        resize_handle.setStyleSheet("padding-right: 5px; padding-bottom: 2px;")
        resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        
        resize_handle.mousePressEvent = lambda e: self._start_resize(e)
        resize_handle.mouseMoveEvent = lambda e: self._do_resize(e, min_height, max_height)
        
        desc_container.addWidget(resize_handle)
        
        self.layout.addWidget(desc_label)
        self.layout.addLayout(desc_container)
        return self.description_input
    
    def add_date_time_field(self, label="Date & Time:"):
        """Add date and time picker fields"""
        datetime_label = QLabel(label)
        self.layout.addWidget(datetime_label)
        
        datetime_row = QHBoxLayout()
        datetime_row.setSpacing(10)
        
        # Date picker
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        # Apply locale settings
        first_day = config.get('locale.week_starts_on', 'Monday')
        calendar_widget = self.date_input.calendarWidget()
        if calendar_widget:
            if first_day == "Sunday":
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
            else:
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        
        datetime_row.addWidget(self.date_input, 1)
        
        # Time picker
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        
        # Set display format based on config
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '12hr':
            self.time_input.setDisplayFormat("hh:mm AP")
        else:
            self.time_input.setDisplayFormat("HH:mm")
        
        datetime_row.addWidget(self.time_input, 0)
        
        self.layout.addLayout(datetime_row)
        return self.date_input, self.time_input
    
    def add_buttons(self, save_text="Save", cancel_text="Cancel", on_save=None):
        """Add save and cancel buttons"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(save_text)
        if on_save:
            save_btn.clicked.connect(on_save)
        else:
            save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        self.layout.addLayout(buttons_layout)
        return save_btn, cancel_btn
    
    def get_datetime(self):
        """Get combined datetime from date and time inputs"""
        if not hasattr(self, 'date_input') or not hasattr(self, 'time_input'):
            return None
        
        from datetime import datetime
        date = self.date_input.date()
        time = self.time_input.time()
        
        return datetime(
            date.year(),
            date.month(),
            date.day(),
            time.hour(),
            time.minute()
        )
    
    def set_datetime(self, dt):
        """Set date and time inputs from datetime object"""
        if not hasattr(self, 'date_input') or not hasattr(self, 'time_input'):
            return
        
        if dt:
            self.date_input.setDate(QDate(dt.year, dt.month, dt.day))
            self.time_input.setTime(QTime(dt.hour, dt.minute))
    
    def _apply_description_styling(self):
        """Apply theme styling to description field"""
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.description_input.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 8px 12px;
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
        """Start resizing description box"""
        self.resize_start_y = event.globalPosition().y()
        self.resize_start_height = self.description_input.height()
    
    def _do_resize(self, event, min_height, max_height):
        """Resize description box"""
        if hasattr(self, 'resize_start_y'):
            delta = event.globalPosition().y() - self.resize_start_y
            new_height = max(min_height, min(max_height, self.resize_start_height + delta))
            self.description_input.setFixedHeight(int(new_height))
