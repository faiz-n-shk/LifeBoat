"""
Todos View
Main todos page with multiple views
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from src.shared.dialogs import NoScrollComboBox

from src.features.todos.controller import TodosController
from src.features.todos.widgets import TodoItem, TodoDialog


class TodosView(QWidget):
    """Todos main view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = TodosController()
        self.current_filter = "all"
        self.current_category = "All"
        self.search_query = ""
        self.setup_ui()
        self.load_todos()
    
    def setup_ui(self):
        """Setup todos UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        header = QLabel("✓ Todos")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Add button
        add_btn = QPushButton("+ New Todo")
        add_btn.clicked.connect(self.on_add_todo)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Stats bar
        self.stats_bar = QFrame()
        self.stats_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        stats_layout = QHBoxLayout(self.stats_bar)
        stats_layout.setSpacing(20)
        
        self.total_label = QLabel("Total: 0")
        self.active_label = QLabel("Active: 0")
        self.completed_label = QLabel("Completed: 0")
        self.today_label = QLabel("Today: 0")
        self.overdue_label = QLabel("Overdue: 0")
        
        for label in [self.total_label, self.active_label, self.completed_label, 
                      self.today_label, self.overdue_label]:
            font = QFont()
            font.setPointSize(10)
            label.setFont(font)
            stats_layout.addWidget(label)
        
        stats_layout.addStretch()
        layout.addWidget(self.stats_bar)
        
        # Filters and search
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Filter dropdown
        filter_label = QLabel("Show:")
        filter_layout.addWidget(filter_label)
        
        self.filter_combo = NoScrollComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed", "Today", "Overdue"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        # Category filter
        category_label = QLabel("Category:")
        filter_layout.addWidget(category_label)
        
        self.category_combo = NoScrollComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search todos...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        # Todos list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.todos_container = QWidget()
        self.todos_layout = QVBoxLayout(self.todos_container)
        self.todos_layout.setSpacing(8)
        self.todos_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.todos_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll.setWidget(self.todos_container)
        layout.addWidget(self.scroll)
        
        self.setLayout(layout)
    
    def load_todos(self):
        """Load and display todos"""
        # Clear existing
        for i in reversed(range(self.todos_layout.count())):
            widget = self.todos_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get todos
        filter_map = {
            "All": "all",
            "Active": "active",
            "Completed": "completed",
            "Today": "today",
            "Overdue": "overdue"
        }
        
        filter_type = filter_map.get(self.current_filter, "all")
        category = None if self.current_category == "All" else self.current_category
        
        todos = self.controller.get_todos(filter_type, category)
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            todos = [t for t in todos if 
                    query_lower in t.title.lower() or 
                    (t.description and query_lower in t.description.lower()) or
                    (t.category and query_lower in t.category.lower()) or
                    (t.tags and query_lower in t.tags.lower())]
        
        # Display todos
        if todos:
            for todo in todos:
                item = TodoItem(todo, self.controller)
                item.edit_requested.connect(self.on_edit_todo)
                item.delete_requested.connect(self.on_delete_todo)
                item.toggle_requested.connect(self.on_toggle_todo)
                self.todos_layout.addWidget(item)
        else:
            empty_label = QLabel("No todos found")
            empty_label.setProperty("class", "secondary-text")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(12)
            empty_label.setFont(font)
            self.todos_layout.addWidget(empty_label)
        
        # Update stats
        self.update_stats()
        
        # Update category filter
        self.update_category_filter()
    
    def update_stats(self):
        """Update statistics display"""
        stats = self.controller.get_stats()
        
        self.total_label.setText(f"Total: {stats['total']}")
        self.active_label.setText(f"Active: {stats['active']}")
        self.completed_label.setText(f"Completed: {stats['completed']}")
        self.today_label.setText(f"Today: {stats['today']}")
        
        overdue_text = f"Overdue: {stats['overdue']}"
        self.overdue_label.setText(overdue_text)
        
        if stats['overdue'] > 0:
            self.overdue_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        else:
            self.overdue_label.setStyleSheet("")
    
    def update_category_filter(self):
        """Update category filter dropdown"""
        current = self.category_combo.currentText()
        
        # Block signals to prevent triggering on_category_changed
        self.category_combo.blockSignals(True)
        
        self.category_combo.clear()
        self.category_combo.addItem("All")
        
        categories = self.controller.get_categories()
        self.category_combo.addItems(categories)
        
        if current in ["All"] + categories:
            self.category_combo.setCurrentText(current)
        
        # Unblock signals
        self.category_combo.blockSignals(False)
    
    def on_filter_changed(self, filter_text):
        """Handle filter change"""
        self.current_filter = filter_text
        self.load_todos()
    
    def on_category_changed(self, category):
        """Handle category change"""
        self.current_category = category
        self.load_todos()
    
    def on_search_changed(self, text):
        """Handle search text change"""
        self.search_query = text
        self.load_todos()
    
    def on_add_todo(self):
        """Handle add todo"""
        dialog = TodoDialog(self, controller=self.controller)
        if dialog.exec():
            data = dialog.get_todo_data()
            if data['title']:
                self.controller.create_todo(data)
                self.load_todos()
    
    def on_edit_todo(self, todo_id):
        """Handle edit todo"""
        from src.core.database import db
        db.connect(reuse_if_open=True)
        from src.models.todo import Todo
        todo = Todo.get_by_id(todo_id)
        db.close()
        
        dialog = TodoDialog(self, todo=todo, controller=self.controller)
        if dialog.exec():
            data = dialog.get_todo_data()
            if data['title']:
                self.controller.update_todo(todo_id, data)
                self.load_todos()
    
    def on_delete_todo(self, todo_id):
        """Handle delete todo"""
        from src.shared.dialogs import create_message_box
        from PyQt6.QtWidgets import QMessageBox
        
        msg = create_message_box(
            self,
            "Confirm Delete",
            "Delete this todo?\n\nThis action cannot be undone.",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.controller.delete_todo(todo_id)
            self.load_todos()
    
    def on_toggle_todo(self, todo_id):
        """Handle toggle todo completion"""
        self.controller.toggle_complete(todo_id)
        self.load_todos()
    
    def refresh(self):
        """Refresh view"""
        self.load_todos()
