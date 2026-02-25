"""
Task Dialog
Dialog for creating/editing tasks
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit,
    QPushButton, QFormLayout
)
from PyQt6.QtCore import Qt, QDateTime

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
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form
        form = QFormLayout()
        form.setSpacing(15)
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title...")
        form.addRow("Title:", self.title_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter description (optional)...")
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        
        # Priority
        self.priority_combo = QComboBox()
        priorities = config.get('tasks.priorities', ["Low", "Medium", "High", "Urgent"])
        self.priority_combo.addItems(priorities)
        self.priority_combo.setCurrentText("Medium")
        form.addRow("Priority:", self.priority_combo)
        
        # Status
        self.status_combo = QComboBox()
        statuses = config.get('tasks.statuses', 
                             ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
        self.status_combo.addItems(statuses)
        form.addRow("Status:", self.status_combo)
        
        # Due date
        self.due_date_input = QDateTimeEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDateTime(QDateTime.currentDateTime())
        
        # Set display format based on user preference
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '24hr':
            self.due_date_input.setDisplayFormat("dd-MM-yyyy HH:mm")
        else:
            self.due_date_input.setDisplayFormat("dd-MM-yyyy hh:mm AP")
        
        form.addRow("Due Date:", self.due_date_input)
        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags (comma-separated)...")
        form.addRow("Tags:", self.tags_input)
        
        layout.addLayout(form)
        
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
        
        self.setLayout(layout)
    
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
            self.due_date_input.setDateTime(QDateTime(self.task.due_date))
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
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'due_date': self.due_date_input.dateTime().toPyDateTime(),
            'tags': self.tags_input.text().strip() or None,
        }
