"""
Goal Item Widget
Individual goal display component
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class GoalItem(QFrame):
    """Widget for displaying a single goal"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    toggle_requested = pyqtSignal(int)
    
    def __init__(self, goal, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.setup_ui()
    
    def setup_ui(self):
        """Setup goal item UI"""
        self.setObjectName("task-item")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header row
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        
        # Title
        title = QLabel(self.goal.title)
        title.setWordWrap(True)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        
        if self.goal.completed:
            title.setProperty("class", "secondary-text")
            title.setStyleSheet("text-decoration: line-through;")
        
        header_row.addWidget(title, 1)
        
        # Complete button
        complete_btn = QPushButton("✓" if not self.goal.completed else "↻")
        complete_btn.setToolTip("Mark as complete" if not self.goal.completed else "Mark as incomplete")
        complete_btn.setFixedSize(30, 30)
        complete_btn.clicked.connect(lambda: self.toggle_requested.emit(self.goal.id))
        header_row.addWidget(complete_btn)
        
        layout.addLayout(header_row)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(self.goal.progress)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat(f"{self.goal.progress}%")
        progress_bar.setFixedHeight(20)
        layout.addWidget(progress_bar)
        
        # Meta info row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(15)
        
        # Category
        if self.goal.category:
            category = QLabel(f"📁 {self.goal.category}")
            category.setProperty("class", "meta-text")
            meta_row.addWidget(category)
        
        # Target date
        if self.goal.target_date:
            from datetime import date
            today = date.today()
            days_left = (self.goal.target_date - today).days
            
            if days_left < 0:
                date_text = f"⏰ Overdue by {abs(days_left)} days"
            elif days_left == 0:
                date_text = "⏰ Due today"
            else:
                date_text = f"📅 {days_left} days left"
            
            target = QLabel(date_text)
            target.setProperty("class", "meta-text")
            meta_row.addWidget(target)
        
        meta_row.addStretch()
        layout.addLayout(meta_row)
        
        # Description (if exists)
        if self.goal.description:
            desc = QLabel(self.goal.description)
            desc.setProperty("class", "secondary-text")
            desc.setWordWrap(True)
            layout.addWidget(desc)
        
        # Action buttons
        actions_row = QHBoxLayout()
        actions_row.addStretch()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.goal.id))
        actions_row.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger-button")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.goal.id))
        actions_row.addWidget(delete_btn)
        
        layout.addLayout(actions_row)
        
        self.setLayout(layout)
