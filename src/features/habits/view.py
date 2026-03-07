"""
Habits View
Habit tracking and streaks with scoring system
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.shared.dialogs import NoScrollComboBox

from src.features.habits.controller import HabitsController
from src.features.habits.widgets.habit_dialog import HabitDialog
from src.features.habits.widgets.habit_item import HabitItem


class HabitsView(QWidget):
    """Habit tracking and management view with scoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = HabitsController()
        self.all_habits = []
        self.setup_ui()
        self.load_habits()
    
    def setup_ui(self):
        """Setup habits UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header row
        header_row = QHBoxLayout()
        
        header = QLabel("🔄 Habits")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header_row.addWidget(header)
        
        header_row.addStretch()
        
        # Score box
        score_box = QFrame()
        score_box.setObjectName("summary-card")
        
        score_box_layout = QHBoxLayout(score_box)
        score_box_layout.setContentsMargins(12, 8, 12, 8)
        score_box_layout.setSpacing(8)
        
        score_label_text = QLabel("Score:")
        score_label_text.setProperty("class", "meta-text")
        score_box_layout.addWidget(score_label_text)
        
        self.score_label = QLabel("0")
        score_font = QFont()
        score_font.setPointSize(16)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setProperty("class", "accent-label")
        score_box_layout.addWidget(self.score_label)
        
        score_box_layout.addWidget(QLabel("|"))
        
        self.good_label = QLabel("✓0")
        self.good_label.setProperty("class", "meta-text")
        score_box_layout.addWidget(self.good_label)
        
        self.bad_label = QLabel("✗0")
        self.bad_label.setProperty("class", "meta-text")
        score_box_layout.addWidget(self.bad_label)
        
        header_row.addWidget(score_box)
        
        # Add habit button
        add_btn = QPushButton("+ New Habit")
        add_btn.clicked.connect(self.add_habit)
        header_row.addWidget(add_btn)
        
        layout.addLayout(header_row)
        
        # Search and filter row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setFixedWidth(25)
        search_row.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search habits...")
        self.search_input.textChanged.connect(self.filter_habits)
        search_row.addWidget(self.search_input, 1)
        
        self.type_filter = NoScrollComboBox()
        self.type_filter.addItems(["All Types", "Good Habits", "Bad Habits"])
        self.type_filter.currentTextChanged.connect(self.filter_habits)
        search_row.addWidget(self.type_filter)
        
        layout.addLayout(search_row)
        
        # Habits container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.habits_container = QWidget()
        self.habits_main_layout = QVBoxLayout(self.habits_container)
        self.habits_main_layout.setSpacing(0)
        self.habits_main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.habits_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def update_score_display(self):
        """Update the score display"""
        score = self.controller.calculate_daily_score()
        self.score_label.setText(str(int(score)))
        
        breakdown = self.controller.get_score_breakdown()
        self.good_label.setText(f"✓{breakdown['good_completed']}/{breakdown['good_total']}")
        self.bad_label.setText(f"✗{breakdown['bad_completed']}/{breakdown['bad_total']}")
    
    def load_habits(self):
        """Load and display habits"""
        self.all_habits = self.controller.get_habits()
        self.update_score_display()
        self.filter_habits()
    
    def filter_habits(self):
        """Filter habits based on search and type"""
        # Clear existing layout
        while self.habits_main_layout.count():
            item = self.habits_main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        search_text = self.search_input.text().lower().strip()
        type_filter = self.type_filter.currentText()
        
        # Filter habits
        filtered_habits = self.all_habits
        
        if type_filter == "Good Habits":
            filtered_habits = [h for h in filtered_habits if h.habit_type == "Good"]
        elif type_filter == "Bad Habits":
            filtered_habits = [h for h in filtered_habits if h.habit_type == "Bad"]
        
        if search_text:
            filtered_habits = [
                h for h in filtered_habits 
                if search_text in h.name.lower() or 
                (h.description and search_text in h.description.lower())
            ]
        
        if not filtered_habits:
            if not self.all_habits:
                empty_label = QLabel("No habits yet. Create your first habit to start tracking!")
            else:
                empty_label = QLabel("No habits match your search.")
            empty_label.setProperty("class", "secondary-text")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(11)
            empty_label.setFont(font)
            self.habits_main_layout.addWidget(empty_label)
            return
        
        # Separate good and bad habits
        good_habits = [h for h in filtered_habits if h.habit_type == "Good"]
        bad_habits = [h for h in filtered_habits if h.habit_type == "Bad"]
        
        # If both types exist and not filtered, show in columns
        if good_habits and bad_habits and type_filter == "All Types":
            columns_layout = QHBoxLayout()
            columns_layout.setSpacing(15)
            
            # Good habits column
            good_column = QWidget()
            good_layout = QVBoxLayout(good_column)
            good_layout.setSpacing(10)
            good_layout.setContentsMargins(0, 0, 0, 0)
            good_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            good_header = QLabel("✓ Good Habits")
            good_header.setProperty("class", "title-text")
            good_layout.addWidget(good_header)
            
            for habit in good_habits:
                habit_item = HabitItem(habit, self.controller)
                habit_item.edit_requested.connect(self.edit_habit)
                habit_item.delete_requested.connect(self.delete_habit)
                good_layout.addWidget(habit_item)
            
            columns_layout.addWidget(good_column, 1)
            
            # Bad habits column
            bad_column = QWidget()
            bad_layout = QVBoxLayout(bad_column)
            bad_layout.setSpacing(10)
            bad_layout.setContentsMargins(0, 0, 0, 0)
            bad_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            bad_header = QLabel("✗ Bad Habits")
            bad_header.setProperty("class", "title-text")
            bad_layout.addWidget(bad_header)
            
            for habit in bad_habits:
                habit_item = HabitItem(habit, self.controller)
                habit_item.edit_requested.connect(self.edit_habit)
                habit_item.delete_requested.connect(self.delete_habit)
                bad_layout.addWidget(habit_item)
            
            columns_layout.addWidget(bad_column, 1)
            
            self.habits_main_layout.addLayout(columns_layout)
        else:
            # Single column
            single_layout = QVBoxLayout()
            single_layout.setSpacing(10)
            single_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            for habit in filtered_habits:
                habit_item = HabitItem(habit, self.controller)
                habit_item.edit_requested.connect(self.edit_habit)
                habit_item.delete_requested.connect(self.delete_habit)
                single_layout.addWidget(habit_item)
            
            self.habits_main_layout.addLayout(single_layout)
    
    def clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
    
    def add_habit(self):
        """Open dialog to add new habit"""
        dialog = HabitDialog(self)
        if dialog.exec():
            data = dialog.get_habit_data()
            if data['name']:
                self.controller.create_habit(**data)
                self.load_habits()
    
    def edit_habit(self, habit_id):
        """Open dialog to edit habit"""
        from src.models.habit import Habit
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            db.close()
            
            dialog = HabitDialog(self, habit=habit)
            if dialog.exec():
                data = dialog.get_habit_data()
                if data['name']:
                    self.controller.update_habit(habit_id, **data)
                    self.load_habits()
        except Exception as e:
            print(f"Error editing habit: {e}")
    
    def delete_habit(self, habit_id):
        """Delete a habit"""
        from src.shared.dialogs import show_question
        from PyQt6.QtWidgets import QMessageBox
        
        reply = show_question(
            self,
            "Delete Habit",
            "Are you sure you want to delete this habit? All tracking data will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_habit(habit_id)
            self.load_habits()
    
    def refresh(self):
        """Refresh view"""
        self.load_habits()
