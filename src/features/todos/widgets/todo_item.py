"""
Todo Item Widget
Individual todo display component
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import date, timedelta

from src.core.config import config


class TodoItem(QFrame):
    """Widget for displaying a single todo"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    toggle_requested = pyqtSignal(int)
    
    def __init__(self, todo, controller, parent=None):
        super().__init__(parent)
        self.todo = todo
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup todo item UI"""
        self.setObjectName("task-item")
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 10, 12, 10)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.todo.completed)
        self.checkbox.setFixedSize(24, 24)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.stateChanged.connect(lambda: self.toggle_requested.emit(self.todo.id))
        main_layout.addWidget(self.checkbox)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title = QLabel(self.todo.title)
        font = QFont()
        font.setPointSize(11)
        if self.todo.completed:
            font.setStrikeOut(True)
        title.setFont(font)
        title.setWordWrap(True)
        title_row.addWidget(title, 1)
        
        # Priority badge
        if self.todo.priority and self.todo.priority != "Medium":
            priority_badge = QLabel(self.todo.priority)
            priority_badge.setProperty("class", "small-text")
            
            if self.todo.priority == "Urgent":
                color = "#dc3545"
            elif self.todo.priority == "High":
                color = "#ffc107"
            else:
                color = "#6c757d"
            
            priority_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 8pt;
                    font-weight: bold;
                }}
            """)
            title_row.addWidget(priority_badge)
        
        content_layout.addLayout(title_row)
        
        # Meta info row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(12)
        
        meta_items = []
        
        # Due date
        if self.todo.due_date:
            due_text = self.format_due_date(self.todo.due_date)
            is_overdue = self.todo.due_date < date.today() and not self.todo.completed
            
            due_label = QLabel(f"📅 {due_text}")
            due_label.setProperty("class", "meta-text")
            
            if is_overdue:
                due_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
            meta_items.append(due_label)
        
        # Category
        if self.todo.category:
            cat_label = QLabel(f"🏷️ {self.todo.category}")
            cat_label.setProperty("class", "meta-text")
            meta_items.append(cat_label)
        
        # Tags
        if self.todo.tags:
            tags = self.todo.get_tags_list()
            if tags:
                tags_text = " ".join([f"#{tag}" for tag in tags[:3]])
                tags_label = QLabel(tags_text)
                tags_label.setProperty("class", "meta-text")
                meta_items.append(tags_label)
        
        for item in meta_items:
            meta_row.addWidget(item)
        
        meta_row.addStretch()
        
        if meta_items:
            content_layout.addLayout(meta_row)
        
        main_layout.addLayout(content_layout, 1)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)
        
        from src.core.path_manager import get_resource_path
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(get_resource_path("assets/icons/edit.svg")))
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("QPushButton { border-radius: 14px; padding: 0px; }")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.todo.id))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path("assets/icons/delete.svg")))
        delete_btn.setFixedSize(28, 28)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setProperty("class", "danger-button")
        delete_btn.setStyleSheet("QPushButton { border-radius: 14px; padding: 0px; }")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.todo.id))
        actions_layout.addWidget(delete_btn)
        
        main_layout.addLayout(actions_layout)
        
        self.setLayout(main_layout)
    
    def format_due_date(self, due_date):
        """Format due date for display"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        if due_date == today:
            return "Today"
        elif due_date == tomorrow:
            return "Tomorrow"
        elif due_date < today:
            days_ago = (today - due_date).days
            return f"{days_ago}d overdue"
        else:
            days_until = (due_date - today).days
            if days_until <= 7:
                return f"in {days_until}d"
            else:
                return due_date.strftime("%b %d")
