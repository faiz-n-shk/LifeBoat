"""
Habit Dialog - Clean 2-column layout
"""
from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, 
    QHBoxLayout, QVBoxLayout, QFrame, QTextEdit,
    QRadioButton, QButtonGroup, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from src.shared.dialogs import NoScrollComboBox, NoScrollSpinBox, BaseDialog
from src.core.path_manager import get_resource_path


class HabitDialog(BaseDialog):
    """Dialog for creating/editing habits"""
    
    def __init__(self, parent=None, habit=None):
        super().__init__(parent, title="Edit Habit" if habit else "Create New Habit", width=950)
        self.habit = habit
        self.selected_color = "#30e86e"
        self.custom_days = 7
        self.color_buttons = []
        self.setup_fields()
        
        if habit:
            self.load_habit_data()
    
    def setup_fields(self):
        """Setup dialog fields"""
        # Create scrollable container
        from PyQt6.QtWidgets import QScrollArea
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Main container with 2 columns
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Font for labels
        label_font = QFont()
        label_font.setPointSize(11)
        label_font.setBold(True)
        
        # Font for inputs
        input_font = QFont()
        input_font.setPointSize(10)
        
        # ========== LEFT COLUMN ==========
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setSpacing(18)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name
        name_lbl = QLabel("Habit Name")
        name_lbl.setFont(label_font)
        left_layout.addWidget(name_lbl)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Drink water")
        self.title_input.setMinimumHeight(40)
        self.title_input.setFont(input_font)
        left_layout.addWidget(self.title_input)
        
        # Type
        type_lbl = QLabel("Habit Type")
        type_lbl.setFont(label_font)
        left_layout.addWidget(type_lbl)
        
        type_frame = QFrame()
        type_frame.setObjectName("habit-type-container")
        type_layout = QHBoxLayout(type_frame)
        type_layout.setContentsMargins(8, 8, 8, 8)
        type_layout.setSpacing(8)
        
        self.type_button_group = QButtonGroup()
        
        self.good_radio = QRadioButton("  Good")
        self.good_radio.setIcon(QIcon(get_resource_path("assets/icons/icon_check.svg")))
        self.good_radio.setIconSize(QSize(16, 16))
        self.good_radio.setObjectName("habit-type-radio")
        self.good_radio.setChecked(True)
        self.good_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.good_radio.toggled.connect(self.update_ui_for_type)
        self.good_radio.setMinimumHeight(44)
        radio_font = QFont()
        radio_font.setPointSize(11)
        self.good_radio.setFont(radio_font)
        self.type_button_group.addButton(self.good_radio, 0)
        type_layout.addWidget(self.good_radio)
        
        self.bad_radio = QRadioButton("  Bad")
        self.bad_radio.setIcon(QIcon(get_resource_path("assets/icons/icon_cross.svg")))
        self.bad_radio.setIconSize(QSize(16, 16))
        self.bad_radio.setObjectName("habit-type-radio")
        self.bad_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bad_radio.setMinimumHeight(44)
        self.bad_radio.setFont(radio_font)
        self.type_button_group.addButton(self.bad_radio, 1)
        type_layout.addWidget(self.bad_radio)
        
        left_layout.addWidget(type_frame)
        
        # Description
        desc_lbl = QLabel("Description (Optional)")
        desc_lbl.setFont(label_font)
        left_layout.addWidget(desc_lbl)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Why do you want to build this habit?")
        self.description_input.setFixedHeight(140)
        self.description_input.setFont(input_font)
        
        # Apply custom styling
        self._apply_description_styling()
        
        left_layout.addWidget(self.description_input)
        
        left_layout.addStretch()
        
        # ========== RIGHT COLUMN ==========
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setSpacing(18)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frequency
        freq_lbl = QLabel("Frequency")
        freq_lbl.setFont(label_font)
        right_layout.addWidget(freq_lbl)
        
        freq_frame = QFrame()
        freq_frame.setObjectName("frequency-box")
        freq_frame.setMaximumWidth(380)
        freq_layout = QHBoxLayout(freq_frame)
        freq_layout.setContentsMargins(12, 10, 12, 10)
        freq_layout.setSpacing(8)
        
        at_least = QLabel("At least")
        at_least.setFont(input_font)
        freq_layout.addWidget(at_least, 0)
        
        self.frequency_count_input = NoScrollSpinBox()
        self.frequency_count_input.setMinimum(1)
        self.frequency_count_input.setMaximum(100)
        self.frequency_count_input.setValue(1)
        self.frequency_count_input.setFixedWidth(70)
        self.frequency_count_input.setMinimumHeight(38)
        self.frequency_count_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frequency_count_input.setFont(input_font)
        freq_layout.addWidget(self.frequency_count_input, 0)
        
        times = QLabel("times per")
        times.setFont(input_font)
        freq_layout.addWidget(times, 0)
        
        self.frequency_period_input = NoScrollComboBox()
        self.frequency_period_input.addItems(["Day", "Week", "Month", "Year"])
        self.frequency_period_input.setCurrentText("Day")
        self.frequency_period_input.setMinimumHeight(38)
        self.frequency_period_input.setFixedWidth(95)
        self.frequency_period_input.setFont(input_font)
        freq_layout.addWidget(self.frequency_period_input, 0)
        
        freq_layout.addStretch(1)
        
        right_layout.addWidget(freq_frame)
        
        # Target Duration
        target_lbl = QLabel("Target Duration")
        target_lbl.setFont(label_font)
        right_layout.addWidget(target_lbl)
        
        self.target_input = NoScrollComboBox()
        self.target_input.addItems([
            "1 Week (7 days)", 
            "1 Month (31 days)", 
            "3 Months (90 days)",
            "6 Months (180 days)",
            "1 Year (365 days)",
            "Custom"
        ])
        self.target_input.setMinimumHeight(40)
        self.target_input.setMaximumWidth(380)
        self.target_input.setFont(input_font)
        self.target_input.currentTextChanged.connect(self.on_target_changed)
        right_layout.addWidget(self.target_input)
        
        # Custom days
        self.custom_days_input = NoScrollSpinBox()
        self.custom_days_input.setMinimum(1)
        self.custom_days_input.setMaximum(365)
        self.custom_days_input.setValue(7)
        self.custom_days_input.setSuffix(" days")
        self.custom_days_input.setMinimumHeight(40)
        self.custom_days_input.setMaximumWidth(380)
        self.custom_days_input.setFont(input_font)
        self.custom_days_input.setVisible(False)
        self.custom_days_input.valueChanged.connect(self.on_custom_days_changed)
        right_layout.addWidget(self.custom_days_input)
        
        # Color
        color_lbl = QLabel("Habit Color")
        color_lbl.setFont(label_font)
        right_layout.addWidget(color_lbl)
        
        colors_widget = QWidget()
        colors_widget.setMaximumWidth(380)
        colors_layout = QHBoxLayout(colors_widget)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        colors_layout.setSpacing(5)
        
        colors = ["#30e86e", "#3b82f6", "#8b5cf6", "#ec4899", "#f97316", "#eab308"]
        
        for color in colors:
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("color_value", color)
            btn.setObjectName("color-swatch")
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            self.color_buttons.append(btn)
            colors_layout.addWidget(btn, 0)
        
        colors_layout.addStretch()
        right_layout.addWidget(colors_widget)
        
        # Custom color picker button (outside container)
        self.custom_color_btn = QPushButton("Pick Custom Color")
        self.custom_color_btn.setMaximumWidth(380)
        self.custom_color_btn.setMinimumHeight(32)
        self.custom_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.custom_color_btn.clicked.connect(self.pick_custom_color)
        right_layout.addWidget(self.custom_color_btn)
        
        right_layout.addStretch()
        
        # Add columns
        main_layout.addWidget(left_col, 1)
        main_layout.addWidget(right_col, 1)
        
        scroll.setWidget(main_container)
        self.layout.addWidget(scroll)
        
        # Buttons
        self.add_buttons(save_text="Save Habit" if not self.habit else "Update Habit")
        
        # Apply styling
        self.update_color_swatches()
        self.update_ui_for_type()
    
    def select_color(self, color):
        """Select color"""
        self.selected_color = color
        self.update_color_swatches()
    
    def pick_custom_color(self):
        """Open color picker dialog"""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Pick Habit Color")
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_swatches()
    
    def _apply_description_styling(self):
        """Apply custom styling to description text editor"""
        try:
            from src.core.config import config
            from src.core.database import db
            from src.models.theme import Theme
            
            theme_name = config.get('appearance.theme', 'Dark')
            if theme_name == "System":
                from src.core.theme_manager import theme_manager
                theme_name = theme_manager.detect_os_theme()
            
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_name)
            db.close()
            
            self.description_input.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {theme_obj.bg_secondary};
                    color: {theme_obj.fg_primary};
                    border: 2px solid {theme_obj.border};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 10pt;
                }}
                QTextEdit::corner {{
                    background-color: {theme_obj.bg_tertiary};
                    border: 1px solid {theme_obj.border};
                }}
            """)
        except:
            pass
    
    def update_color_swatches(self):
        """Update color swatch styling"""
        for btn in self.color_buttons:
            color = btn.property("color_value")
            is_selected = (color == self.selected_color)
            
            if is_selected:
                btn.setStyleSheet(f"""
                    QPushButton#color-swatch {{
                        background-color: {color};
                        border: 2px solid {color};
                        border-radius: 11px;
                        outline: 2px solid {color}70;
                        outline-offset: 1px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton#color-swatch {{
                        background-color: {color};
                        border: 1px solid transparent;
                        border-radius: 11px;
                    }}
                    QPushButton#color-swatch:hover {{
                        border: 2px solid {color};
                    }}
                """)
    
    def update_ui_for_type(self):
        """Update UI for habit type"""
        # Only set default colors for NEW habits, not when editing existing ones
        if not self.habit:
            # Only change color if user hasn't manually selected one yet
            # Check if current color is one of the defaults
            if self.selected_color in ["#30e86e", "#ef4444"]:
                if self.good_radio.isChecked():
                    self.selected_color = "#30e86e"
                else:
                    self.selected_color = "#ef4444"
                self.update_color_swatches()
    
    def on_target_changed(self, text):
        """Handle target change"""
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
        """Handle custom days change"""
        self.custom_days = value
    
    def load_habit_data(self):
        """Load habit data"""
        if not self.habit:
            return
        
        self.title_input.setText(self.habit.name)
        
        if self.habit.habit_type == "Good":
            self.good_radio.setChecked(True)
        else:
            self.bad_radio.setChecked(True)
        
        if hasattr(self.habit, 'frequency_count') and hasattr(self.habit, 'frequency_period'):
            self.frequency_count_input.setValue(self.habit.frequency_count)
            period_map = {"day": "Day", "week": "Week", "month": "Month", "year": "Year"}
            self.frequency_period_input.setCurrentText(period_map.get(self.habit.frequency_period, "Day"))
        
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
            self.update_color_swatches()
        
        if self.habit.description:
            self.description_input.setPlainText(self.habit.description)
    
    def get_habit_data(self):
        """Get habit data"""
        period_map = {"Day": "day", "Week": "week", "Month": "month", "Year": "year"}
        
        return {
            'name': self.title_input.text().strip(),
            'habit_type': "Good" if self.good_radio.isChecked() else "Bad",
            'target_days': self.custom_days,
            'color': self.selected_color,
            'description': self.description_input.toPlainText().strip() or None,
            'frequency_count': self.frequency_count_input.value(),
            'frequency_period': period_map[self.frequency_period_input.currentText()]
        }
