"""
Tasks View
Main tasks management page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox
)
from PyQt6.QtCore import Qt

from src.features.tasks.controller import TasksController
from src.features.tasks.widgets.task_item import TaskItem
from src.features.tasks.widgets.task_dialog import TaskDialog


class TasksView(QWidget):
    """Tasks main view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = TasksController()
        self.task_items = []
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """Setup tasks UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        
        title = QLabel("✓ Tasks")
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.filter_combo)
        
        # Add task button
        add_btn = QPushButton("+ Add Task")
        add_btn.clicked.connect(self.on_add_task)
        header_layout.addWidget(add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tasks list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setSpacing(10)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.tasks_container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def load_tasks(self):
        """Load tasks from database"""
        # Clear existing
        for item in self.task_items:
            item.deleteLater()
        self.task_items.clear()
        
        # Get filter
        filter_type = self.filter_combo.currentText()
        
        # Load tasks
        tasks = self.controller.get_tasks(filter_type)
        
        if not tasks:
            # Show empty state
            empty_label = QLabel("No tasks yet. Click '+ Add Task' to create one.")
            empty_label.setProperty("class", "secondary-text")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tasks_layout.addWidget(empty_label)
            self.task_items.append(empty_label)
        else:
            # Create task items
            for task in tasks:
                task_item = TaskItem(task, self)
                task_item.task_updated.connect(self.on_task_updated)
                task_item.task_deleted.connect(self.on_task_deleted)
                self.tasks_layout.addWidget(task_item)
                self.task_items.append(task_item)
    
    def on_add_task(self):
        """Handle add task button click"""
        dialog = TaskDialog(self)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.controller.create_task(task_data)
            self.load_tasks()
    
    def on_task_updated(self, task_id: int):
        """Handle task update"""
        self.load_tasks()
    
    def on_task_deleted(self, task_id: int):
        """Handle task deletion"""
        self.controller.delete_task(task_id)
        self.load_tasks()
    
    def on_filter_changed(self, filter_type: str):
        """Handle filter change"""
        self.load_tasks()
    
    def refresh(self):
        """Refresh view to apply config changes"""
        self.load_tasks()
