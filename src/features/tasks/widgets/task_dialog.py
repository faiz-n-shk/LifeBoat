"""
Task Dialog
Dialog for creating/editing tasks
"""
from PyQt6.QtWidgets import QLabel, QComboBox, QLineEdit
from PyQt6.QtCore import QDate, QTime
from src.shared.dialogs import NoScrollComboBox, NoScrollDateEdit

from src.models.task import Task
from src.core.config import config
from src.shared.dialogs import BaseDialog


class TaskDialog(BaseDialog):
    """Dialog for creating or editing a task"""
    
    def __init__(self, parent=None, task: Task = None):
        self.task = task
        self.is_edit = task is not None
        
        title = "Edit Task" if self.is_edit else "New Task"
        super().__init__(parent, title=title, width=500, height=550)
        
        self.setup_fields()
        
        if self.is_edit:
            self.load_task_data()
    
    def setup_fields(self):
        """Setup task-specific fields"""
        # Title
        self.add_title_field(placeholder="Enter task title...")
        
        # Description
        self.add_description_field()
        
        # Priority
        priority_label = QLabel("Priority:")
        self.priority_combo = NoScrollComboBox()
        priorities = config.get('tasks.priorities', ["Low", "Medium", "High", "Urgent"])
        self.priority_combo.addItems(priorities)
        self.priority_combo.setCurrentText("Medium")
        self.layout.addWidget(priority_label)
        self.layout.addWidget(self.priority_combo)
        
        # Status
        status_label = QLabel("Status:")
        self.status_combo = NoScrollComboBox()
        statuses = config.get('tasks.statuses', 
                             ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
        self.status_combo.addItems(statuses)
        self.layout.addWidget(status_label)
        self.layout.addWidget(self.status_combo)
        
        # Due date and time
        self.add_date_time_field(label="Due Date & Time:")
        
        # Tags
        tags_label = QLabel("Tags:")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags (comma-separated)...")
        self.layout.addWidget(tags_label)
        self.layout.addWidget(self.tags_input)
        
        # Buttons
        save_text = "Save" if self.is_edit else "Create"
        self.add_buttons(save_text=save_text, on_save=self.on_save)
    
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
            self.set_datetime(self.task.due_date)
        if self.task.tags:
            self.tags_input.setText(self.task.tags)
    
    def on_save(self):
        """Handle save button click"""
        if not self.title_input.text().strip():
            from src.shared.dialogs import show_warning
            show_warning(self, "Validation Error", "Please enter a task title.")
            return
        
        self.accept()
    
    def get_task_data(self):
        """Get task data from form"""
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'due_date': self.get_datetime(),
            'tags': self.tags_input.text().strip() or None,
        }
