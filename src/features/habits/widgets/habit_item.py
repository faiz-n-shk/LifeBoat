"""
Habit Item Widget - Clean implementation
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
from datetime import date, timedelta

from src.core.config import config
from src.core.path_manager import get_resource_path


class HabitItem(QFrame):
    """Modern habit card widget"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, habit, controller, parent=None):
        super().__init__(parent)
        self.habit = habit
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup habit card UI"""
        self.setObjectName("habit-card")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 18, 20, 18)
        
        # Top row
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        # Get data
        freq_count = getattr(self.habit, 'frequency_count', 1)
        freq_period = getattr(self.habit, 'frequency_period', 'day')
        current_count = self.controller.get_today_count(self.habit.id)
        is_goal_met = self.controller.is_completed_today(self.habit.id)
        
        # Counter or check button
        if freq_count > 1:
            # Segmented control - seamless design with dividers
            from PyQt6.QtGui import QFontMetrics
            from PyQt6.QtWidgets import QLayout
            
            # Calculate dynamic sizes based on font metrics
            base_font = QFont()
            base_font.setPointSize(14)
            fm = QFontMetrics(base_font)
            em = fm.height()
            
            button_size = int(em * 2.8)
            label_width = int(em * 3.2)
            container_height = int(em * 2.8)
            
            self.counter_widget = QFrame()
            self.counter_widget.setObjectName("counter_container")
            # Let the layout handle the size!
            
            counter_layout = QHBoxLayout(self.counter_widget)
            counter_layout.setContentsMargins(0, 0, 0, 0)
            counter_layout.setSpacing(0)
            # Force the container to shrink-wrap the fixed kids
            counter_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
            
            # Decrement button
            self.decrement_btn = QPushButton()
            self.decrement_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_minus.svg")))
            self.decrement_btn.setIconSize(QSize(int(em * 1.2), int(em * 1.2)))
            self.decrement_btn.setFixedSize(button_size, container_height)
            self.decrement_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.decrement_btn.clicked.connect(self.on_decrement)
            counter_layout.addWidget(self.decrement_btn)
            
            # Count label
            self.count_label = QLabel(f"{current_count}/{freq_count}")
            self.count_label.setFixedSize(label_width, container_height)
            self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_font = QFont()
            count_font.setPointSize(14)
            count_font.setBold(True)
            self.count_label.setFont(count_font)
            counter_layout.addWidget(self.count_label)
            
            # Increment button
            self.increment_btn = QPushButton()
            self.increment_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_plus.svg")))
            self.increment_btn.setIconSize(QSize(int(em * 1.2), int(em * 1.2)))
            self.increment_btn.setFixedSize(button_size, container_height)
            self.increment_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.increment_btn.clicked.connect(self.on_increment)
            counter_layout.addWidget(self.increment_btn)
            
            # Style
            self.apply_counter_style(is_goal_met, current_count, freq_count)
            top_row.addWidget(self.counter_widget)
        else:
            # Simple check button - match counter box width
            from PyQt6.QtGui import QFontMetrics
            
            base_font = QFont()
            base_font.setPointSize(14)
            fm = QFontMetrics(base_font)
            em = fm.height()
            
            # Use EXACT same calculation as counter box
            button_size = int(em * 2.8)
            label_width = int(em * 3.2)
            check_width = button_size * 2 + label_width  # 8.8em total
            check_height = int(em * 2.8)
            icon_size = int(em * 1.4)
            
            self.check_btn = QPushButton()
            self.check_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_check.svg")))
            self.check_btn.setIconSize(QSize(icon_size, icon_size))
            self.check_btn.setFixedSize(check_width, check_height)
            self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.check_btn.clicked.connect(self.on_toggle_check)
            
            if is_goal_met:
                self.check_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.habit.color};
                        color: white;
                        border: 2px solid {self.habit.color};
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.habit.color}DD;
                    }}
                """)
            else:
                self.check_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {self.habit.color};
                        border: 2px solid {self.habit.color};
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.habit.color}22;
                    }}
                """)
            
            top_row.addWidget(self.check_btn)
        
        top_row.addSpacing(16)
        
        # Title
        title_container = QVBoxLayout()
        title_container.setSpacing(3)
        
        title = QLabel(self.habit.name)
        title.setWordWrap(False)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title_container.addWidget(title)
        
        # Goal
        is_bad_habit = self.habit.habit_type == "Bad"
        period_names = {'day': 'day', 'week': 'week', 'month': 'month', 'year': 'year'}
        
        if freq_count > 1 or freq_period != 'day':
            if is_bad_habit:
                goal_text = f"Goal: Less than {freq_count}x per {period_names.get(freq_period, 'day')}"
            else:
                goal_text = f"Goal: At least {freq_count}x per {period_names.get(freq_period, 'day')}"
        else:
            if is_bad_habit:
                goal_text = f"Goal: Avoid daily"
            else:
                goal_text = f"Goal: Daily habit"
        
        goal_label = QLabel(goal_text)
        goal_label.setProperty("class", "secondary-text")
        goal_font = QFont()
        goal_font.setPointSize(9)
        goal_label.setFont(goal_font)
        title_container.addWidget(goal_label)
        
        top_row.addLayout(title_container, 1)
        
        # Actions
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_edit.svg")))
        edit_btn.setIconSize(QSize(18, 18))
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setObjectName("habit-action-btn")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.habit.id))
        top_row.addWidget(edit_btn)
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_delete.svg")))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setObjectName("habit-action-btn-danger")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.habit.id))
        top_row.addWidget(delete_btn)
        
        layout.addLayout(top_row)
        
        # Bottom row: Week + Streak
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        
        # Week
        week_container = QHBoxLayout()
        week_container.setSpacing(6)
        
        today = date.today()
        logs = self.controller.get_habit_logs(self.habit.id, days=7)
        
        week_starts_on = config.get('datetime.week_start', 'Monday')
        today_weekday = today.weekday()
        
        if week_starts_on == "Sunday":
            days_back = (today_weekday + 1) % 7
        else:
            days_back = today_weekday
        
        week_start = today - timedelta(days=days_back)
        
        for i in range(7):
            check_date = week_start + timedelta(days=i)
            
            # Get the log for this day
            day_log = next((log for log in logs if log.date == check_date), None)
            
            # For bad habits, check if count is below goal
            is_bad_habit = self.habit.habit_type == "Bad"
            if day_log:
                count = getattr(day_log, 'count', 1) if day_log.completed else 0
                if is_bad_habit:
                    is_success = count < freq_count
                else:
                    is_success = count >= freq_count
            else:
                # No log means 0 count
                if is_bad_habit:
                    is_success = True  # Didn't do it = success for bad habit
                else:
                    is_success = False  # Didn't do it = failure for good habit
            
            day_indicator = QLabel()
            day_indicator.setFixedSize(32, 32)
            day_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_indicator.setText(check_date.strftime("%a")[0])
            
            if check_date > today:
                day_indicator.setStyleSheet(f"""
                    QLabel {{
                        background-color: transparent;
                        border: 2px solid {self.habit.color}50;
                        border-radius: 16px;
                        color: {self.habit.color}AA;
                        font-size: 10pt;
                        font-weight: 700;
                    }}
                """)
            elif is_success:
                day_indicator.setStyleSheet(f"""
                    QLabel {{
                        background-color: {self.habit.color};
                        border: 2px solid {self.habit.color};
                        border-radius: 16px;
                        color: #ffffff;
                        font-size: 10pt;
                        font-weight: bold;
                    }}
                """)
            else:
                day_indicator.setStyleSheet(f"""
                    QLabel {{
                        background-color: transparent;
                        border: 2px solid {self.habit.color};
                        border-radius: 16px;
                        color: {self.habit.color};
                        font-size: 10pt;
                        font-weight: 700;
                    }}
                """)
            
            week_container.addWidget(day_indicator)
        
        bottom_row.addLayout(week_container)
        bottom_row.addStretch()
        
        # Streak - show current streak or yesterday's streak if today not done
        current_streak = self.controller.get_current_streak(self.habit.id)
        is_today_complete = self.controller.is_completed_today(self.habit.id)
        is_bad_habit = self.habit.habit_type == "Bad"
        
        # For daily habits, check yesterday if today not complete
        if freq_period == 'day':
            # If today is not complete and streak is 0, check from yesterday
            if not is_today_complete and current_streak == 0:
                # Calculate streak from yesterday
                yesterday = date.today() - timedelta(days=1)
                
                # Check if yesterday was complete
                yesterday_log = None
                for log in self.controller.get_habit_logs(self.habit.id, days=2):
                    if log.date == yesterday:
                        yesterday_log = log
                        break
                
                if yesterday_log:
                    freq_count = getattr(self.habit, 'frequency_count', 1)
                    count = getattr(yesterday_log, 'count', 1) if yesterday_log.completed else 0
                    
                    if is_bad_habit:
                        yesterday_complete = count < freq_count
                    else:
                        yesterday_complete = count >= freq_count
                    
                    if yesterday_complete:
                        # Count streak from yesterday backwards
                        temp_streak = 0
                        check_date = yesterday
                        for i in range(365):
                            log = None
                            for l in self.controller.get_habit_logs(self.habit.id, days=i+2):
                                if l.date == check_date:
                                    log = l
                                    break
                            
                            if log:
                                count = getattr(log, 'count', 1) if log.completed else 0
                                if is_bad_habit:
                                    goal_met = count < freq_count
                                else:
                                    goal_met = count >= freq_count
                                
                                if goal_met:
                                    temp_streak += 1
                                    check_date -= timedelta(days=1)
                                else:
                                    break
                            else:
                                if is_bad_habit:
                                    temp_streak += 1
                                    check_date -= timedelta(days=1)
                                else:
                                    break
                        
                        current_streak = temp_streak
        
        # Show streak display
        streak_container = QVBoxLayout()
        streak_container.setSpacing(0)
        streak_container.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Streak header with icon
        streak_header = QHBoxLayout()
        streak_header.setSpacing(4)
        streak_header.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Icon selection
        streak_icon = QLabel()
        from PyQt6.QtGui import QPixmap
        
        # Get current count to check if threshold was exceeded
        current_count = self.controller.get_today_count(self.habit.id)
        
        # For non-daily periods, show different behavior
        if freq_period != 'day':
            if is_bad_habit:
                # Bad habit: fire when stayed below threshold, timer when went over
                if current_count >= freq_count:
                    # Went over threshold - broken
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
                elif is_today_complete or current_streak > 0:
                    # Stayed below threshold - success
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_fire.svg"))
                else:
                    # Not tracked yet
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
            else:
                # Good habit: fire when goal met, timer when not met
                if is_today_complete:
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_fire.svg"))
                else:
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
        else:
            # Daily habits
            if is_bad_habit:
                # Bad habit: fire when stayed below threshold, timer when went over
                if current_count >= freq_count:
                    # Went over threshold - broken
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
                elif is_today_complete or current_streak > 0:
                    # Stayed below threshold - success
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_fire.svg"))
                else:
                    # Not tracked yet
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
            else:
                # Good habit: fire when complete, timer when not complete
                if is_today_complete:
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_fire.svg"))
                else:
                    pixmap = QPixmap(get_resource_path("assets/icons/icon_habit-timer.svg"))
        
        streak_icon.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation))
        streak_icon.setFixedSize(16, 16)
        streak_header.addWidget(streak_icon)
        
        streak_label = QLabel("STREAK")
        streak_label.setProperty("class", "secondary-text")
        streak_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        streak_font = QFont()
        streak_font.setPointSize(7)
        streak_font.setBold(True)
        streak_label.setFont(streak_font)
        streak_header.addWidget(streak_label)
        
        streak_container.addLayout(streak_header)
        
        # Streak value text
        if freq_period != 'day':
            # Non-daily periods
            if is_bad_habit:
                # Bad habit: stayed below threshold = success
                current_count = self.controller.get_today_count(self.habit.id)
                if is_today_complete and current_streak > 0:
                    # Stayed below threshold, has streak
                    period_unit = {'week': 'Week', 'month': 'Month', 'year': 'Year'}.get(freq_period, 'Period')
                    plural_unit = period_unit + 's' if current_streak > 1 else period_unit
                    streak_text = f"{current_streak} {plural_unit}"
                elif current_count >= freq_count:
                    # Went over the threshold - streak broken
                    streak_text = "Streak broken"
                elif is_today_complete:
                    # Stayed below but no streak yet
                    streak_text = "0 Periods"
                else:
                    # Not tracked yet, show current streak or on hold
                    if current_streak > 0:
                        period_unit = {'week': 'Week', 'month': 'Month', 'year': 'Year'}.get(freq_period, 'Period')
                        plural_unit = period_unit + 's' if current_streak > 1 else period_unit
                        streak_text = f"{current_streak} {plural_unit}"
                    else:
                        streak_text = "On hold till complete"
            else:
                # Good habit: if goal met, show streak; if not met, on hold
                if is_today_complete and current_streak > 0:
                    period_unit = {'week': 'Week', 'month': 'Month', 'year': 'Year'}.get(freq_period, 'Period')
                    plural_unit = period_unit + 's' if current_streak > 1 else period_unit
                    streak_text = f"{current_streak} {plural_unit}"
                else:
                    streak_text = "On hold till complete"
        else:
            # Daily habits
            if is_bad_habit:
                # Bad habit: stayed below threshold = success
                current_count = self.controller.get_today_count(self.habit.id)
                if current_streak > 0:
                    streak_text = f"{current_streak} {'Day' if current_streak == 1 else 'Days'}"
                elif current_count >= freq_count:
                    # Went over the threshold - streak broken
                    streak_text = "Streak broken"
                else:
                    # Not done yet or stayed below with no previous streak
                    if is_today_complete:
                        streak_text = "0 Days"
                    else:
                        # Period not over yet, show on hold
                        streak_text = "On hold till complete"
            else:
                # Good habit: if completed, show streak; if not, on hold
                if current_streak > 0:
                    streak_text = f"{current_streak} {'Day' if current_streak == 1 else 'Days'}"
                elif not is_today_complete:
                    streak_text = "On hold till complete"
                else:
                    streak_text = "0 Days"
        
        streak_value = QLabel(streak_text)
        streak_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        streak_value_font = QFont()
        streak_value_font.setPointSize(11)
        streak_value_font.setBold(True)
        streak_value.setFont(streak_value_font)
        streak_container.addWidget(streak_value)
        
        bottom_row.addLayout(streak_container)
        
        layout.addLayout(bottom_row)
    
    def apply_counter_style(self, is_goal_met, current_count, freq_count):
        """Apply seamless segmented control styling with dividers and progressive opacity"""
        from src.core.theme_manager import theme_manager
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        
        if is_goal_met:
            # Completed - full opacity habit color
            bg_color = self.habit.color
            text_color = "white"
            divider_color = "rgba(255, 255, 255, 0.3)"
            hover_color = "rgba(255, 255, 255, 0.15)"
            border_style = f"2px solid {self.habit.color}"
        else:
            # Not completed - progressive opacity based on count
            # Calculate opacity: 0.3 at 0 count, 1.0 at full count
            if freq_count > 0:
                progress = current_count / freq_count
                opacity = 0.3 + (progress * 0.7)  # Range from 0.3 to 1.0
            else:
                opacity = 0.3
            
            # Convert hex color to rgba with opacity
            hex_color = self.habit.color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            bg_color = f"rgba({r}, {g}, {b}, {opacity})"
            text_color = "white" if opacity > 0.6 else theme.fg_primary if theme else "#ffffff"
            divider_color = f"rgba(255, 255, 255, 0.3)" if opacity > 0.6 else (theme.border if theme else "#444444")
            hover_color = f"rgba(255, 255, 255, 0.15)" if opacity > 0.6 else (theme.bg_tertiary if theme else "#3a3a3a")
            border_style = f"2px solid {self.habit.color}"
        
        # Container with rounded corners and border
        self.counter_widget.setStyleSheet(f"""
            QFrame#counter_container {{
                background-color: {bg_color};
                border-radius: 10px;
                border: {border_style};
            }}
        """)
        
        # Left button with right divider - only round left corners
        self.decrement_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-right: 1px solid {divider_color};
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                color: {text_color};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        
        # Middle label with dividers on both sides - no rounding
        self.count_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {text_color};
                border: none;
                border-right: 1px solid {divider_color};
                border-radius: 0px;
            }}
        """)
        
        # Right button - only round right corners
        self.increment_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                color: {text_color};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
    
    def on_increment(self):
        """Handle increment"""
        self.controller.increment_habit(self.habit.id)
        # Reload view to update streak
        parent = self.parent()
        while parent:
            if hasattr(parent, 'load_habits'):
                parent.load_habits()
                return
            parent = parent.parent()
    
    def on_decrement(self):
        """Handle decrement"""
        self.controller.decrement_habit(self.habit.id)
        # Reload view to update streak
        parent = self.parent()
        while parent:
            if hasattr(parent, 'load_habits'):
                parent.load_habits()
                return
            parent = parent.parent()
    
    def on_toggle_check(self):
        """Handle toggle for 1x frequency habits"""
        is_completed = self.controller.is_completed_today(self.habit.id)
        
        if is_completed:
            # Uncheck: decrement to 0
            self.controller.decrement_habit(self.habit.id)
        else:
            # Check: increment to 1
            self.controller.increment_habit(self.habit.id)
        
        # Reload view
        parent = self.parent()
        while parent:
            if hasattr(parent, 'load_habits'):
                parent.load_habits()
                return
            parent = parent.parent()
