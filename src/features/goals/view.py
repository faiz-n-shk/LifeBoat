"""
Goals View
Goals tracking and management
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.features.goals.controller import GoalsController
from src.features.goals.widgets.goal_dialog import GoalDialog
from src.features.goals.widgets.goal_item import GoalItem


class GoalsView(QWidget):
    """Goals tracking and management view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = GoalsController()
        self.setup_ui()
        self.load_goals()
    
    def setup_ui(self):
        """Setup goals UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_row = QHBoxLayout()
        
        header = QLabel("🎯 Goals")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header_row.addWidget(header)
        
        header_row.addStretch()
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Goals", "Active", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.load_goals)
        header_row.addWidget(self.filter_combo)
        
        # Add goal button
        add_btn = QPushButton("+ New Goal")
        add_btn.clicked.connect(self.add_goal)
        header_row.addWidget(add_btn)
        
        layout.addLayout(header_row)
        
        # Goals list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.goals_container = QWidget()
        self.goals_layout = QVBoxLayout(self.goals_container)
        self.goals_layout.setSpacing(15)
        self.goals_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.goals_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def load_goals(self):
        """Load and display goals"""
        # Clear existing goals
        while self.goals_layout.count():
            item = self.goals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get filter
        filter_text = self.filter_combo.currentText()
        completed = None
        if filter_text == "Active":
            completed = False
        elif filter_text == "Completed":
            completed = True
        
        # Load goals
        goals = self.controller.get_goals(completed=completed)
        
        if not goals:
            empty_label = QLabel("No goals yet. Create your first goal!")
            empty_label.setProperty("class", "secondary-text")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(12)
            empty_label.setFont(font)
            self.goals_layout.addWidget(empty_label)
            return
        
        # Display goals
        for goal in goals:
            goal_item = GoalItem(goal)
            goal_item.edit_requested.connect(self.edit_goal)
            goal_item.delete_requested.connect(self.delete_goal)
            goal_item.toggle_requested.connect(self.toggle_complete)
            self.goals_layout.addWidget(goal_item)
    
    def add_goal(self):
        """Open dialog to add new goal"""
        dialog = GoalDialog(self)
        if dialog.exec():
            data = dialog.get_goal_data()
            if data['title']:
                self.controller.create_goal(**data)
                self.load_goals()
    
    def edit_goal(self, goal_id):
        """Open dialog to edit goal"""
        from src.models.goal import Goal
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.get_by_id(goal_id)
            db.close()
            
            dialog = GoalDialog(self, goal=goal)
            if dialog.exec():
                data = dialog.get_goal_data()
                if data['title']:
                    self.controller.update_goal(goal_id, **data)
                    self.load_goals()
        except Exception as e:
            print(f"Error editing goal: {e}")
    
    def delete_goal(self, goal_id):
        """Delete a goal"""
        reply = QMessageBox.question(
            self,
            "Delete Goal",
            "Are you sure you want to delete this goal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_goal(goal_id)
            self.load_goals()
    
    def toggle_complete(self, goal_id):
        """Toggle goal completion status"""
        self.controller.toggle_complete(goal_id)
        self.load_goals()
    
    def refresh(self):
        """Refresh view"""
        self.load_goals()

