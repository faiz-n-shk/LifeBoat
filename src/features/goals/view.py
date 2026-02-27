"""
Goals View
Goals tracking and management
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from src.shared.dialogs import NoScrollComboBox

from src.features.goals.controller import GoalsController
from src.features.goals.widgets.goal_dialog import GoalDialog
from src.features.goals.widgets.goal_item import GoalItem


class GoalsView(QWidget):
    """Goals tracking and management view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = GoalsController()
        self.goal_items = []
        self.initial_load = True
        self.setup_ui()
        QTimer.singleShot(100, self.load_data_with_animation)
    
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
        self.filter_combo = NoScrollComboBox()
        self.filter_combo.addItems(["All Goals", "Active", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.load_data_with_animation)
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
    
    def load_data_with_animation(self):
        """Load goals and trigger animations"""
        from src.core.config import config
        
        # Reset all progress to 0 before loading
        if config.get('appearance.enable_animations', True) and self.initial_load:
            for goal_item in self.goal_items:
                goal_item._progress = 0
                goal_item._target_progress = 0
                goal_item.update()
        
        self.load_data()
    
    def load_data(self):
        """Load goals from database"""
        from src.core.config import config
        should_animate = config.get('appearance.enable_animations', True) and self.initial_load
        self.initial_load = False
        
        # Clear existing goals
        while self.goals_layout.count():
            item = self.goals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.goal_items = []
        
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
        
        # Create goal items
        for goal in goals:
            goal_item = GoalItem(goal)
            goal_item.edit_requested.connect(self.edit_goal)
            goal_item.delete_requested.connect(self.delete_goal)
            goal_item.progress_updated.connect(self.update_progress)
            self.goals_layout.addWidget(goal_item)
            self.goal_items.append(goal_item)
        
        # Force layout update before setting progress
        self.goals_container.updateGeometry()
        
        # Set progress with animation after a delay to ensure widgets are sized
        QTimer.singleShot(100, lambda: self.set_all_progress(should_animate))
    
    def set_all_progress(self, animate):
        """Set progress for all goal items"""
        for goal_item in self.goal_items:
            goal_item.set_progress(goal_item.goal.progress, animate=animate)
    
    def showEvent(self, event):
        """Handle show event to trigger animations"""
        super().showEvent(event)
        
        from src.core.config import config
        if config.get('appearance.enable_animations', True):
            for goal_item in self.goal_items:
                goal_item._progress = 0
                goal_item._target_progress = 0
                goal_item.update()
        
        self.initial_load = True
        QTimer.singleShot(50, self.load_data_with_animation)
    
    def add_goal(self):
        """Open dialog to add new goal"""
        dialog = GoalDialog(self)
        if dialog.exec():
            data = dialog.get_goal_data()
            if data['title']:
                self.controller.create_goal(**data)
                # Reload without animation
                self.load_data()
    
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
                    # Reload without animation
                    self.load_data()
        except Exception as e:
            print(f"Error editing goal: {e}")
    
    def delete_goal(self, goal_id):
        """Delete a goal"""
        from src.shared.dialogs import show_question
        from PyQt6.QtWidgets import QMessageBox
        
        reply = show_question(
            self,
            "Delete Goal",
            "Are you sure you want to delete this goal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_goal(goal_id)
            # Reload without animation
            self.load_data()
    
    def update_progress(self, goal_id, new_progress):
        """Update goal progress"""
        result = self.controller.update_progress(goal_id, new_progress)
        if result:
            # Find the goal item and update it directly without reloading
            for goal_item in self.goal_items:
                if goal_item.goal.id == goal_id:
                    # Update the goal object
                    goal_item.goal.progress = new_progress
                    goal_item.goal.completed = result.completed
                    
                    # Update the display directly
                    goal_item._progress = new_progress
                    goal_item._target_progress = new_progress
                    goal_item.update()
                    
                    # Check if goal should be hidden based on current filter
                    filter_text = self.filter_combo.currentText()
                    should_hide = False
                    
                    if filter_text == "Active" and result.completed:
                        should_hide = True
                    elif filter_text == "Completed" and not result.completed:
                        should_hide = True
                    
                    if should_hide:
                        # Reload to apply filter
                        self.load_data()
                    
                    break
    
    def refresh(self):
        """Refresh view"""
        from src.core.config import config
        if config.get('appearance.enable_animations', True):
            for goal_item in self.goal_items:
                goal_item._progress = 0
                goal_item._target_progress = 0
                goal_item.update()
        
        self.initial_load = True
        self.load_data_with_animation()
