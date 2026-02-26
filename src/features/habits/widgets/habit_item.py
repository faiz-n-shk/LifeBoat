"""
Habit Item Widget
Individual habit display component with streak tracking
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import date, timedelta

from src.core.config import config


class HabitItem(QFrame):
    """Widget for displaying a single habit with completion tracking"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    log_requested = pyqtSignal(int)
    
    def __init__(self, habit, controller, parent=None):
        super().__init__(parent)
        self.habit = habit
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup habit item UI"""
        self.setObjectName("task-item")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Top row: Check button + Title
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        # Check button (smaller)
        is_completed = self.controller.is_completed_today(self.habit.id)
        check_btn = QPushButton()
        check_btn.setFixedSize(36, 36)
        check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if is_completed:
            check_btn.setText("✓")
            check_btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 16pt;
                    background-color: {self.habit.color};
                    border: none;
                    border-radius: 18px;
                    color: white;
                    font-weight: bold;
                    min-width: 36px;
                    max-width: 36px;
                    min-height: 36px;
                    max-height: 36px;
                }}
                QPushButton:hover {{
                    opacity: 0.85;
                }}
                QPushButton:pressed {{
                    background-color: {self.habit.color};
                }}
            """)
        else:
            check_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 2px solid {self.habit.color};
                    border-radius: 18px;
                    min-width: 36px;
                    max-width: 36px;
                    min-height: 36px;
                    max-height: 36px;
                }}
                QPushButton:hover {{
                    background-color: {self.habit.color};
                    opacity: 0.2;
                }}
                QPushButton:pressed {{
                    background-color: transparent;
                    border: 2px solid {self.habit.color};
                }}
            """)
        
        check_btn.clicked.connect(lambda: self.log_requested.emit(self.habit.id))
        top_row.addWidget(check_btn)
        
        # Title
        title = QLabel(self.habit.name)
        title.setWordWrap(False)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        title.setFont(font)
        top_row.addWidget(title, 1)
        
        from src.core.path_manager import get_resource_path
        
        # Action buttons (inline)
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(get_resource_path("assets/icons/edit.svg")))
        edit_btn.setFixedSize(24, 24)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("QPushButton { border-radius: 12px; padding: 0px; }")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.habit.id))
        top_row.addWidget(edit_btn)
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path("assets/icons/delete.svg")))
        delete_btn.setFixedSize(24, 24)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setProperty("class", "danger-button")
        delete_btn.setStyleSheet("QPushButton { border-radius: 12px; padding: 0px; }")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.habit.id))
        top_row.addWidget(delete_btn)
        
        layout.addLayout(top_row)
        
        # Progress row
        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)
        
        days_completed = self.controller.get_days_completed(self.habit.id)
        days_remaining = self.controller.get_days_remaining(self.habit.id)
        
        if days_remaining > 0:
            progress_label = QLabel(f"{days_completed}/{self.habit.target_days}")
            progress_label.setProperty("class", "meta-text")
            progress_row.addWidget(progress_label)
            
            remaining_label = QLabel(f"{days_remaining} left")
            remaining_label.setProperty("class", "meta-text")
            progress_row.addWidget(remaining_label)
        else:
            completion_label = QLabel("✓ Completed")
            completion_label.setProperty("class", "active-label")
            progress_row.addWidget(completion_label)
        
        # Streak
        streak = self.controller.get_current_streak(self.habit.id)
        if streak > 0:
            streak_label = QLabel(f"🔥 {streak}")
            streak_label.setProperty("class", "meta-text")
            progress_row.addWidget(streak_label)
        
        progress_row.addStretch()
        layout.addLayout(progress_row)
        
        # 7-day mini history with day labels (respecting week start setting)
        days_row = QHBoxLayout()
        days_row.setSpacing(4)
        
        today = date.today()
        logs = self.controller.get_habit_logs(self.habit.id, days=7)
        
        # Get week start setting
        week_starts_on = config.get('locale.week_starts_on', 'Monday')
        
        # Calculate the start of the current week
        today_weekday = today.weekday()  # Monday = 0, Tuesday = 1, ..., Sunday = 6
        
        if week_starts_on == "Sunday":
            # Week starts on Sunday
            # If today is Sunday (6), days_back = 0
            # If today is Monday (0), days_back = 1
            # If today is Saturday (5), days_back = 6
            days_back = (today_weekday + 1) % 7
        else:
            # Week starts on Monday (default)
            # If today is Monday (0), days_back = 0
            # If today is Sunday (6), days_back = 6
            days_back = today_weekday
        
        week_start = today - timedelta(days=days_back)
        
        # Show 7 days from week start
        for i in range(7):
            check_date = week_start + timedelta(days=i)
            
            # Check if this day has been completed
            completed = any(log.date == check_date and log.completed for log in logs)
            
            day_container = QVBoxLayout()
            day_container.setSpacing(2)
            
            # Day letter
            day_letter = QLabel(check_date.strftime("%a")[0])
            day_letter.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Highlight today
            if check_date == today:
                day_letter.setStyleSheet("font-size: 7pt; color: #fff; font-weight: bold;")
            else:
                day_letter.setStyleSheet("font-size: 7pt; color: #888;")
            
            day_container.addWidget(day_letter)
            
            # Status indicator (styled box)
            indicator = QLabel()
            indicator.setFixedSize(14, 14)
            indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # For bad habits, invert the logic: success = NOT completed
            is_bad_habit = self.habit.habit_type == "Bad"
            is_success = (not completed) if is_bad_habit else completed
            
            # Gray out future days
            if check_date > today:
                indicator.setStyleSheet("""
                    background-color: transparent;
                    border: 2px solid #444;
                    border-radius: 7px;
                """)
            elif is_success:
                indicator.setStyleSheet(f"""
                    background-color: {self.habit.color};
                    border-radius: 7px;
                    border: none;
                """)
            else:
                indicator.setStyleSheet(f"""
                    background-color: transparent;
                    border: 3px solid #888;
                    border-radius: 7px;
                """)
            
            day_container.addWidget(indicator)
            days_row.addLayout(day_container)
        
        days_row.addStretch()
        layout.addLayout(days_row)
        
        self.setLayout(layout)
