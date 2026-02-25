"""
Habit Dialog
Dialog for creating and editing habits
"""
from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QHBoxLayout, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.shared.dialogs import BaseDialog


class HabitDialog(BaseDialog):
    """Dialog for creating/editing habits"""
    
    def __init__(self, parent=None, habit=None):
        super().__init__(parent, title="Edit Habit" if habit else "New Habit", width=450, height=550)
        self.habit = habit
        self.selected_color = "#0078d4"
        self.custom_days = 7
        self.setup_fields()
        
        if habit:
            self.load_habit_data()
    
    def setup_fields(self):
        """Setup dialog fields"""
        # Name
        self.add_title_field(label="Habit Name:", placeholder="Enter habit name...")
        
        # Habit Type
        type_label = QLabel("Habit Type:")
        self.type_input = QComboBox()
        self.type_input.addItems(["Good", "Bad"])
        self.type_input.currentTextChanged.connect(self.update_ui_for_type)
        self.layout.addWidget(type_label)
        self.layout.addWidget(self.type_input)
        
        # Target Duration
        self.target_label = QLabel("Target Duration:")
        self.layout.addWidget(self.target_label)
        
        self.target_input = QComboBox()
        self.target_input.addItems([
            "1 Week (7 days)", 
            "1 Month (31 days)", 
            "3 Months (90 days)",
            "6 Months (180 days)",
            "1 Year (365 days)",
            "Custom"
        ])
        self.target_input.currentTextChanged.connect(self.on_target_changed)
        self.layout.addWidget(self.target_input)
        
        # Custom days input (hidden by default)
        self.custom_days_input = QSpinBox()
        self.custom_days_input.setMinimum(1)
        self.custom_days_input.setMaximum(365)
        self.custom_days_input.setValue(7)
        self.custom_days_input.setSuffix(" days (max 365)")
        self.custom_days_input.setVisible(False)
        self.custom_days_input.valueChanged.connect(self.on_custom_days_changed)
        self.layout.addWidget(self.custom_days_input)
        
        # Color picker
        color_label = QLabel("Color:")
        self.layout.addWidget(color_label)
        
        color_row = QHBoxLayout()
        color_row.setSpacing(10)
        
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(40, 40)
        self.update_color_preview(self.selected_color)
        color_row.addWidget(self.color_preview)
        
        pick_color_btn = QPushButton("Choose Color")
        pick_color_btn.clicked.connect(self.pick_color)
        color_row.addWidget(pick_color_btn, 1)
        
        self.layout.addLayout(color_row)
        
        # Description
        self.add_description_field(
            label="Description:",
            placeholder="Enter habit description (optional)...",
            min_height=60,
            max_height=120
        )
        
        # Buttons
        self.add_buttons(save_text="Save Habit" if not self.habit else "Update Habit")
        
        # Set initial placeholder
        self.update_ui_for_type("Good")
    
    def update_ui_for_type(self, habit_type):
        """Update UI based on habit type"""
        if habit_type == "Good":
            self.target_label.setText("Goal Duration (to build good habits or unbuild bad ones):")
            if not self.habit:
                self.selected_color = "#28a745"
                self.update_color_preview(self.selected_color)
        else:
            self.target_label.setText("Goal Duration (to break habit):")
            if not self.habit:
                self.selected_color = "#dc3545"
                self.update_color_preview(self.selected_color)
    
    def on_target_changed(self, text):
        """Handle target duration change"""
        if text == "Custom":
            self.custom_days_input.setVisible(True)
            self.custom_days = self.custom_days_input.value()
        else:
            self.custom_days_input.setVisible(False)
            if "7" in text:
                self.custom_days = 7
            elif "31" in text:
                self.custom_days = 31
            elif "90" in text:
                self.custom_days = 90
            elif "180" in text:
                self.custom_days = 180
            elif "365" in text:
                self.custom_days = 365
    
    def on_custom_days_changed(self, value):
        """Handle custom days value change"""
        self.custom_days = value
    
    def pick_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Choose Habit Color")
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_preview(self.selected_color)
    
    def update_color_preview(self, color):
        """Update color preview button"""
        self.color_preview.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #888;
                border-radius: 6px;
            }}
        """)
    
    def load_habit_data(self):
        """Load existing habit data into fields"""
        if not self.habit:
            return
        
        self.title_input.setText(self.habit.name)
        self.type_input.setCurrentText(self.habit.habit_type)
        
        # Set target duration
        if self.habit.target_days == 7:
            self.target_input.setCurrentText("1 Week (7 days)")
        elif self.habit.target_days == 31:
            self.target_input.setCurrentText("1 Month (31 days)")
        elif self.habit.target_days == 90:
            self.target_input.setCurrentText("3 Months (90 days)")
        elif self.habit.target_days == 180:
            self.target_input.setCurrentText("6 Months (180 days)")
        elif self.habit.target_days == 365:
            self.target_input.setCurrentText("1 Year (365 days)")
        else:
            self.target_input.setCurrentText("Custom")
            self.custom_days_input.setValue(self.habit.target_days)
            self.custom_days = self.habit.target_days
        
        if self.habit.color:
            self.selected_color = self.habit.color
            self.update_color_preview(self.selected_color)
        
        if self.habit.description:
            self.description_input.setPlainText(self.habit.description)
    
    def get_habit_data(self):
        """Get habit data from dialog fields"""
        return {
            'name': self.title_input.text().strip(),
            'habit_type': self.type_input.currentText(),
            'target_days': self.custom_days,
            'color': self.selected_color,
            'description': self.description_input.toPlainText().strip() or None
        }
