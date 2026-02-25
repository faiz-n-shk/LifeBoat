"""
Task Item Widget
Individual task display
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.models.task import Task
from src.features.tasks.controller import TasksController


class TaskItem(QFrame):
    """Widget for displaying a single task"""
    
    task_updated = pyqtSignal(int)  # task_id
    task_deleted = pyqtSignal(int)  # task_id
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.controller = TasksController()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup task item UI"""
        self.setObjectName("task-item")
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.task.completed)
        self.checkbox.stateChanged.connect(self.on_toggle_complete)
        main_layout.addWidget(self.checkbox)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(self.task.title)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        if self.task.completed:
            self.title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; "
                "text-decoration: line-through; color: #b0b0b0;"
            )
        info_layout.addWidget(self.title_label)
        
        # Metadata
        meta_parts = []
        if self.task.priority:
            meta_parts.append(f"Priority: {self.task.priority}")
        if self.task.status:
            meta_parts.append(f"Status: {self.task.status}")
        if self.task.due_date:
            meta_parts.append(f"Due: {self.task.due_date.strftime('%Y-%m-%d')}")
        
        if meta_parts:
            meta_label = QLabel(" • ".join(meta_parts))
            meta_label.setProperty("class", "meta-text")
            info_layout.addWidget(meta_label)
        
        main_layout.addLayout(info_layout, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(60)
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger-button")
        delete_btn.setFixedWidth(60)
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        main_layout.addLayout(actions_layout)
        
        self.setLayout(main_layout)
    
    def on_toggle_complete(self, state):
        """Handle checkbox toggle"""
        self.controller.toggle_complete(self.task.id)
        self.task_updated.emit(self.task.id)
    
    def on_edit(self):
        """Handle edit button click"""
        from src.features.tasks.widgets.task_dialog import TaskDialog
        dialog = TaskDialog(self, self.task)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.controller.update_task(self.task.id, task_data)
            self.task_updated.emit(self.task.id)
    
    def on_delete(self):
        """Handle delete button click"""
        self.task_deleted.emit(self.task.id)
