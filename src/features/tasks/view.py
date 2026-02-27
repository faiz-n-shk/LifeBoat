"""
Tasks View
Notion-style tasks interface with multiple view modes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.shared.dialogs import NoScrollComboBox

from src.features.tasks.controller import TasksController
from src.features.tasks.widgets.task_dialog import TaskDialog
from src.features.tasks.widgets.task_item import TaskItem


class TasksView(QWidget):
    """Tasks view with multiple display modes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = TasksController()
        self.current_view = "list"  # list, board, table
        self.current_filter = "all"  # all, active, completed
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """Setup tasks UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        
        # Title
        title = QLabel("Tasks")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header.addWidget(title)
        
        header.addStretch()
        
        # View selector
        view_label = QLabel("View:")
        header.addWidget(view_label)
        
        self.view_combo = NoScrollComboBox()
        self.view_combo.addItems(["📋 List", "📊 Board", "📑 Table"])
        self.view_combo.currentIndexChanged.connect(self.on_view_changed)
        header.addWidget(self.view_combo)
        
        # Filter
        filter_label = QLabel("Filter:")
        header.addWidget(filter_label)
        
        self.filter_combo = NoScrollComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        header.addWidget(self.filter_combo)
        
        # Add task button
        add_btn = QPushButton("+ New Task")
        add_btn.clicked.connect(self.on_add_task)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Content area (will hold different views)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.content_container, 1)
        
        self.setLayout(layout)
    
    def on_view_changed(self, index):
        """Handle view mode change"""
        views = ["list", "board", "table"]
        self.current_view = views[index]
        self.load_tasks()
    
    def on_filter_changed(self, filter_text):
        """Handle filter change"""
        self.current_filter = filter_text.lower()
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks in current view mode"""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get filtered tasks
        tasks = self.get_filtered_tasks()
        
        if self.current_view == "list":
            self.show_list_view(tasks)
        elif self.current_view == "board":
            self.show_board_view(tasks)
        else:
            self.show_table_view(tasks)
    
    def get_filtered_tasks(self):
        """Get tasks based on current filter"""
        all_tasks = self.controller.get_tasks()
        
        if self.current_filter == "active":
            return [t for t in all_tasks if not t.completed]
        elif self.current_filter == "completed":
            return [t for t in all_tasks if t.completed]
        else:
            return all_tasks
    
    def show_list_view(self, tasks):
        """Show tasks in list view"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        list_layout.setSpacing(10)
        
        if not tasks:
            no_tasks = QLabel("No tasks found")
            no_tasks.setProperty("class", "secondary-text")
            no_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            list_layout.addWidget(no_tasks)
        else:
            for task in tasks:
                item = TaskItem(task, self)
                item.task_updated.connect(self.on_task_updated)
                item.task_deleted.connect(self.on_task_deleted)
                list_layout.addWidget(item)
        
        scroll.setWidget(list_widget)
        self.content_layout.addWidget(scroll)
    
    def show_board_view(self, tasks):
        """Show tasks in Kanban board view"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        board_widget = QWidget()
        board_layout = QHBoxLayout(board_widget)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        board_layout.setSpacing(15)
        
        # Group tasks by status
        from src.core.config import config
        statuses = config.get('tasks.statuses', 
                             ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
        
        for status in statuses:
            column = self.create_board_column(status, [t for t in tasks if t.status == status])
            board_layout.addWidget(column)
        
        board_layout.addStretch()
        
        scroll.setWidget(board_widget)
        self.content_layout.addWidget(scroll)
    
    def create_board_column(self, status, tasks):
        """Create a column for board view"""
        column = QFrame()
        column.setObjectName("settings-section")
        column.setMinimumWidth(280)
        column.setMaximumWidth(350)
        
        layout = QVBoxLayout(column)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Column header
        header = QLabel(f"{status} ({len(tasks)})")
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        header.setFont(font)
        layout.addWidget(header)
        
        # Scroll area for tasks in this column
        column_scroll = QScrollArea()
        column_scroll.setWidgetResizable(True)
        column_scroll.setFrameShape(QFrame.Shape.NoFrame)
        column_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        column_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        tasks_container = QWidget()
        tasks_layout = QVBoxLayout(tasks_container)
        tasks_layout.setSpacing(10)
        tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Tasks in column
        for task in tasks:
            item = TaskItem(task, self)
            item.task_updated.connect(self.on_task_updated)
            item.task_deleted.connect(self.on_task_deleted)
            tasks_layout.addWidget(item)
        
        if not tasks:
            empty_label = QLabel("No tasks")
            empty_label.setProperty("class", "secondary-text")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tasks_layout.addWidget(empty_label)
        
        column_scroll.setWidget(tasks_container)
        layout.addWidget(column_scroll, 1)
        
        return column
    
    def show_table_view(self, tasks):
        """Show tasks in table view"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setSpacing(0)
        
        # Table header
        header_frame = QFrame()
        header_frame.setObjectName("settings-section")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        headers = [("Title", 3), ("Priority", 1), ("Status", 1), ("Due Date", 1), ("Actions", 1)]
        for header_text, stretch in headers:
            label = QLabel(header_text)
            font = QFont()
            font.setBold(True)
            label.setFont(font)
            header_layout.addWidget(label, stretch)
        
        table_layout.addWidget(header_frame)
        
        # Table rows
        if not tasks:
            no_tasks = QLabel("No tasks found")
            no_tasks.setProperty("class", "secondary-text")
            no_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            table_layout.addWidget(no_tasks)
        else:
            for task in tasks:
                row = self.create_table_row(task)
                table_layout.addWidget(row)
        
        table_layout.addStretch()
        
        scroll.setWidget(table_widget)
        self.content_layout.addWidget(scroll)
    
    def create_table_row(self, task):
        """Create a row for table view"""
        row_frame = QFrame()
        row_frame.setObjectName("task-item")
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(task.title)
        if task.completed:
            title_label.setStyleSheet("text-decoration: line-through; color: #b0b0b0;")
        row_layout.addWidget(title_label, 3)
        
        # Priority
        priority_label = QLabel(task.priority or "-")
        priority_label.setProperty("class", "meta-text")
        row_layout.addWidget(priority_label, 1)
        
        # Status
        status_label = QLabel(task.status or "-")
        status_label.setProperty("class", "meta-text")
        row_layout.addWidget(status_label, 1)
        
        # Due date
        due_label = QLabel(task.due_date.strftime("%Y-%m-%d") if task.due_date else "-")
        due_label.setProperty("class", "meta-text")
        row_layout.addWidget(due_label, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.on_edit_task(task))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger-button")
        delete_btn.clicked.connect(lambda: self.on_delete_task(task))
        actions_layout.addWidget(delete_btn)
        
        row_layout.addLayout(actions_layout, 1)
        
        return row_frame
    
    def on_add_task(self):
        """Handle add task button"""
        dialog = TaskDialog(self)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.controller.create_task(task_data)
            self.load_tasks()
    
    def on_edit_task(self, task):
        """Handle edit task"""
        dialog = TaskDialog(self, task)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.controller.update_task(task.id, task_data)
            self.load_tasks()
    
    def on_delete_task(self, task):
        """Handle delete task"""
        from src.shared.dialogs import create_message_box
        from PyQt6.QtWidgets import QMessageBox
        
        msg = create_message_box(
            self,
            "Confirm Delete",
            f"Delete task '{task.title}'?",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.controller.delete_task(task.id)
            self.load_tasks()
    
    def on_task_updated(self, task_id):
        """Handle task update"""
        self.load_tasks()
    
    def on_task_deleted(self, task_id):
        """Handle task deletion"""
        self.load_tasks()
