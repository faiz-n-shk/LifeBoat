"""
Todo Dialog
Dialog for creating and editing todos
"""
from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QDate
from datetime import date
from src.shared.dialogs import NoScrollComboBox, NoScrollDateEdit

from src.shared.dialogs import BaseDialog
from src.core.config import config


class TodoDialog(BaseDialog):
    """Dialog for creating/editing todos"""
    
    def __init__(self, parent=None, todo=None, controller=None):
        super().__init__(parent, title="Edit Todo" if todo else "New Todo", width=500, height=550)
        self.todo = todo
        self.controller = controller
        self.setup_fields()
        
        if todo:
            self.load_todo_data()
    
    def setup_fields(self):
        """Setup dialog fields"""
        # Title
        self.add_title_field(label="Title:", placeholder="Enter todo title...")
        
        # Priority
        priority_label = QLabel("Priority:")
        self.layout.addWidget(priority_label)
        
        self.priority_input = NoScrollComboBox()
        priorities = config.get('tasks.priorities', ['Low', 'Medium', 'High', 'Urgent'])
        self.priority_input.addItems(priorities)
        self.priority_input.setCurrentText("Medium")
        self.layout.addWidget(self.priority_input)
        
        # Due Date
        due_label = QLabel("Due Date:")
        self.layout.addWidget(due_label)
        
        due_row = QHBoxLayout()
        due_row.setSpacing(10)
        
        self.due_date_input = NoScrollDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
        self.due_date_input.setDisplayFormat("dd-MM-yyyy")
        due_row.addWidget(self.due_date_input, 1)
        
        self.clear_due_btn = QPushButton("Clear")
        self.clear_due_btn.clicked.connect(self.clear_due_date)
        due_row.addWidget(self.clear_due_btn)
        
        self.layout.addLayout(due_row)
        
        # Category
        category_label = QLabel("Category:")
        self.layout.addWidget(category_label)
        
        self.category_input = NoScrollComboBox()
        self.category_input.setEditable(True)
        
        # Load existing categories
        if self.controller:
            categories = self.controller.get_categories()
            self.category_input.addItem("")
            self.category_input.addItems(categories)
        
        self.layout.addWidget(self.category_input)
        
        # Tags
        tags_label = QLabel("Tags (comma-separated):")
        self.layout.addWidget(tags_label)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("work, urgent, personal...")
        self.layout.addWidget(self.tags_input)
        
        # Description
        self.add_description_field(
            label="Description:",
            placeholder="Enter todo description (optional)...",
            min_height=80,
            max_height=150
        )
        
        # Buttons
        self.add_buttons(save_text="Save Todo" if not self.todo else "Update Todo")
    
    def clear_due_date(self):
        """Clear due date"""
        self.due_date_input.setDate(QDate.currentDate())
    
    def load_todo_data(self):
        """Load existing todo data into fields"""
        if not self.todo:
            return
        
        self.title_input.setText(self.todo.title)
        self.priority_input.setCurrentText(self.todo.priority)
        
        if self.todo.due_date:
            qdate = QDate(self.todo.due_date.year, self.todo.due_date.month, self.todo.due_date.day)
            self.due_date_input.setDate(qdate)
        
        if self.todo.category:
            self.category_input.setCurrentText(self.todo.category)
        
        if self.todo.tags:
            self.tags_input.setText(self.todo.tags)
        
        if self.todo.description:
            self.description_input.setPlainText(self.todo.description)
    
    def get_todo_data(self):
        """Get todo data from dialog fields"""
        due_date = self.due_date_input.date().toPyDate()
        
        # Don't save due date if it's today and wasn't set before
        if not self.todo and due_date == date.today():
            due_date = None
        
        category = self.category_input.currentText().strip()
        tags = self.tags_input.text().strip()
        
        return {
            'title': self.title_input.text().strip(),
            'priority': self.priority_input.currentText(),
            'due_date': due_date,
            'category': category if category else None,
            'tags': tags if tags else None,
            'description': self.description_input.toPlainText().strip() or None
        }
