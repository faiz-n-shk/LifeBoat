"""
Goal Dialog
Dialog for creating and editing goals
"""
from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QDateEdit, QHBoxLayout, QSlider
from PyQt6.QtCore import QDate, Qt

from src.shared.dialogs import BaseDialog


class GoalDialog(BaseDialog):
    """Dialog for creating/editing goals"""
    
    def __init__(self, parent=None, goal=None):
        super().__init__(parent, title="Edit Goal" if goal else "New Goal", width=450, height=550)
        self.goal = goal
        self.setup_fields()
        
        if goal:
            self.load_goal_data()
    
    def setup_fields(self):
        """Setup dialog fields"""
        # Title
        self.add_title_field(label="Goal Title:", placeholder="Enter goal title...")
        
        # Category
        category_label = QLabel("Category:")
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "Personal",
            "Career",
            "Health",
            "Finance",
            "Education",
            "Relationships",
            "Other"
        ])
        self.layout.addWidget(category_label)
        self.layout.addWidget(self.category_input)
        
        # Target Date
        date_label = QLabel("Target Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate().addMonths(1))
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_input)
        
        # Progress (only show when editing)
        if self.goal:
            progress_label = QLabel("Progress:")
            self.layout.addWidget(progress_label)
            
            progress_row = QHBoxLayout()
            progress_row.setSpacing(10)
            
            self.progress_slider = QSlider(Qt.Orientation.Horizontal)
            self.progress_slider.setMinimum(0)
            self.progress_slider.setMaximum(100)
            self.progress_slider.setValue(0)
            self.progress_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            self.progress_slider.setTickInterval(10)
            self.progress_slider.valueChanged.connect(self.update_progress_label)
            progress_row.addWidget(self.progress_slider, 1)
            
            self.progress_label = QLabel("0%")
            self.progress_label.setFixedWidth(40)
            self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            progress_row.addWidget(self.progress_label)
            
            self.layout.addLayout(progress_row)
        
        # Description
        self.add_description_field(
            label="Description:",
            placeholder="Enter goal description (optional)..."
        )
        
        # Buttons
        self.add_buttons(save_text="Save Goal" if not self.goal else "Update Goal")
    
    def update_progress_label(self, value):
        """Update progress label when slider changes"""
        self.progress_label.setText(f"{value}%")
    
    def load_goal_data(self):
        """Load existing goal data into fields"""
        if not self.goal:
            return
        
        self.title_input.setText(self.goal.title)
        
        if self.goal.category:
            self.category_input.setCurrentText(self.goal.category)
        
        if self.goal.target_date:
            self.date_input.setDate(QDate(
                self.goal.target_date.year,
                self.goal.target_date.month,
                self.goal.target_date.day
            ))
        
        if hasattr(self, 'progress_slider'):
            self.progress_slider.setValue(self.goal.progress)
        
        if self.goal.description:
            self.description_input.setPlainText(self.goal.description)
    
    def get_goal_data(self):
        """Get goal data from dialog fields"""
        from datetime import date
        
        target_date = self.date_input.date()
        
        data = {
            'title': self.title_input.text().strip(),
            'category': self.category_input.currentText().strip() or None,
            'target_date': date(target_date.year(), target_date.month(), target_date.day()),
            'description': self.description_input.toPlainText().strip() or None
        }
        
        if hasattr(self, 'progress_slider'):
            data['progress'] = self.progress_slider.value()
        
        return data
