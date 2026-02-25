"""
Task Dialog
Dialog for creating/editing tasks
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit,
    QPushButton, QScrollArea, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from PyQt6.QtGui import QPixmap

from src.models.task import Task
from src.core.config import config


class TaskDialog(QDialog):
    """Dialog for creating or editing a task"""
    
    def __init__(self, parent=None, task: Task = None):
        super().__init__(parent)
        self.task = task
        self.is_edit = task is not None
        self.setup_ui()
        
        if self.is_edit:
            self.load_task_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Edit Task" if self.is_edit else "New Task")
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title...")
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # Description
        desc_label = QLabel("Description:")
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(60)
        self.description_input.setMaximumHeight(200)
        self.description_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.description_input.setPlaceholderText("Enter description (optional)...")
        
        # Force visible border with inline stylesheet
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
                """)
                db.close()
            except:
                pass
        
        # Add resize handle indicator
        desc_container = QVBoxLayout()
        desc_container.setSpacing(0)
        desc_container.addWidget(self.description_input)
        
        # Create a custom resize handle with icon
        resize_handle = QLabel()
        pixmap = QPixmap("assets/icons/resize-grip.svg")
        resize_handle.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        resize_handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        resize_handle.setFixedHeight(20)
        resize_handle.setStyleSheet("padding-right: 5px; padding-bottom: 2px;")
        resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        
        # Make description resizable by dragging
        resize_handle.mousePressEvent = lambda e: self.start_resize(e)
        resize_handle.mouseMoveEvent = lambda e: self.do_resize(e)
        
        desc_container.addWidget(resize_handle)
        
        layout.addWidget(desc_label)
        layout.addLayout(desc_container)
        
        # Priority
        priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        priorities = config.get('tasks.priorities', ["Low", "Medium", "High", "Urgent"])
        self.priority_combo.addItems(priorities)
        self.priority_combo.setCurrentText("Medium")
        layout.addWidget(priority_label)
        layout.addWidget(self.priority_combo)
        
        # Status
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        statuses = config.get('tasks.statuses', 
                             ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
        self.status_combo.addItems(statuses)
        layout.addWidget(status_label)
        layout.addWidget(self.status_combo)
        
        # Due date and time
        due_label = QLabel("Due Date & Time:")
        layout.addWidget(due_label)
        
        datetime_row = QHBoxLayout()
        datetime_row.setSpacing(10)
        
        from PyQt6.QtWidgets import QDateEdit, QTimeEdit
        from PyQt6.QtCore import QDate, QTime
        
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
        
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        
        # Set display format based on config
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '12hr':
            self.time_input.setDisplayFormat("hh:mm AP")
        else:
            self.time_input.setDisplayFormat("HH:mm")
        
        datetime_row.addWidget(self.time_input, 0)
        
        layout.addLayout(datetime_row)
        
        # Tags
        tags_label = QLabel("Tags:")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags (comma-separated)...")
        layout.addWidget(tags_label)
        layout.addWidget(self.tags_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save" if self.is_edit else "Create")
        save_btn.clicked.connect(self.on_save)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Set content widget and add to scroll area
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def load_task_data(self):
        """Load existing task data into form"""
        self.title_input.setText(self.task.title)
        if self.task.description:
            self.description_input.setPlainText(self.task.description)
        if self.task.priority:
            self.priority_combo.setCurrentText(self.task.priority)
        if self.task.status:
            self.status_combo.setCurrentText(self.task.status)
        if self.task.due_date:
            self.date_input.setDate(QDate(
                self.task.due_date.year,
                self.task.due_date.month,
                self.task.due_date.day
            ))
            self.time_input.setTime(QTime(
                self.task.due_date.hour,
                self.task.due_date.minute
            ))
        if self.task.tags:
            self.tags_input.setText(self.task.tags)
    
    def on_save(self):
        """Handle save button click"""
        if not self.title_input.text().strip():
            # TODO: Show error message
            return
        
        self.accept()
    
    def get_task_data(self):
        """Get task data from form"""
        # Combine date and time
        date = self.date_input.date()
        time = self.time_input.time()
        
        from datetime import datetime
        due_datetime = datetime(
            date.year(),
            date.month(),
            date.day(),
            time.hour(),
            time.minute()
        )
        
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'due_date': due_datetime,
            'tags': self.tags_input.text().strip() or None,
        }
    
    def start_resize(self, event):
        """Start resizing description box"""
        self.resize_start_y = event.globalPosition().y()
        self.resize_start_height = self.description_input.height()
    
    def do_resize(self, event):
        """Resize description box"""
        if hasattr(self, 'resize_start_y'):
            delta = event.globalPosition().y() - self.resize_start_y
            new_height = max(60, min(200, self.resize_start_height + delta))
            self.description_input.setFixedHeight(int(new_height))
