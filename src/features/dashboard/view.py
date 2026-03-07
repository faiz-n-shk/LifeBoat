"""
Dashboard View
Main overview page with charts and statistics
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap
from datetime import datetime, timedelta

from src.features.dashboard.widgets import StatCard, ProgressRing, ExpensePieChart


class DashboardView(QWidget):
    """Dashboard main view with animated charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Dashboard icon (themed)
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_accent_icon
        
        self.header_icon_label = QLabel()
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/feature_dashboard.svg"), size=(28, 28))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)
        header_layout.addWidget(self.header_icon_label)
        
        header = QLabel("Dashboard")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header_layout.addWidget(header)
        
        # Welcome message with time
        self.welcome_label = QLabel()
        font = QFont()
        font.setPointSize(11)
        self.welcome_label.setFont(font)
        self.welcome_label.setProperty("class", "secondary-text")
        self.update_welcome_message()
        header_layout.addStretch()
        header_layout.addWidget(self.welcome_label)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Summary cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Create animated stat cards
        self.events_card = StatCard("Upcoming Events", "icon_calendar.svg")
        self.habits_card = StatCard("Active Habits", "icon_heart-check.svg")
        self.notes_card = StatCard("Total Notes", "feature_notes.svg")
        self.expenses_card = StatCard("Expenses This Month", "feature_expenses.svg")
        
        cards_layout.addWidget(self.events_card)
        cards_layout.addWidget(self.habits_card)
        cards_layout.addWidget(self.notes_card)
        cards_layout.addWidget(self.expenses_card)
        
        content_layout.addLayout(cards_layout)
        
        # Two column layout for progress and expenses
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)
        
        # Progress section (left)
        progress_section = QFrame()
        progress_section.setObjectName("dashboard-section")
        progress_section.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
        """)
        progress_layout = QVBoxLayout(progress_section)
        progress_layout.setSpacing(15)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title with icon
        section_header = QHBoxLayout()
        
        progress_icon = QLabel()
        from src.shared.icon_utils import load_themed_icon
        progress_icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_progress.svg"), size=(20, 20))
        progress_icon.setPixmap(progress_icon_pixmap)
        section_header.addWidget(progress_icon)
        
        section_title = QLabel("Progress Overview")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        section_title.setFont(font)
        section_header.addWidget(section_title)
        section_header.addStretch()
        
        progress_layout.addLayout(section_header)
        
        # Progress rings in 2x2 grid
        rings_grid = QGridLayout()
        rings_grid.setSpacing(15)
        rings_grid.setHorizontalSpacing(20)
        
        # Top row: Habits Total, Habits Today
        self.habits_total_ring = ProgressRing("Habits Streak")
        self.habits_today_ring = ProgressRing("Habits Today")
        
        rings_grid.addWidget(self.habits_total_ring, 0, 0)
        rings_grid.addWidget(self.habits_today_ring, 0, 1)
        
        # Bottom row: Events, Expenses
        self.events_ring = ProgressRing("Events This Week")
        self.expenses_ring = ProgressRing("Balance Usage")
        
        rings_grid.addWidget(self.events_ring, 1, 0)
        rings_grid.addWidget(self.expenses_ring, 1, 1)
        
        progress_layout.addLayout(rings_grid)
        charts_row.addWidget(progress_section, 1)
        
        # Expense chart section (right)
        expense_section = QFrame()
        expense_section.setObjectName("dashboard-section")
        expense_section.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
        """)
        expense_layout = QVBoxLayout(expense_section)
        expense_layout.setSpacing(15)
        expense_layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title with icon
        expense_header = QHBoxLayout()
        
        expense_icon = QLabel()
        from src.shared.icon_utils import load_themed_icon
        expense_icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_money-pieChart.svg"), size=(20, 20))
        expense_icon.setPixmap(expense_icon_pixmap)
        expense_header.addWidget(expense_icon)
        
        expense_title = QLabel("Expenses by Category")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        expense_title.setFont(font)
        expense_header.addWidget(expense_title)
        expense_header.addStretch()
        
        expense_layout.addLayout(expense_header)
        
        self.expense_chart = ExpensePieChart()
        expense_layout.addWidget(self.expense_chart)
        
        charts_row.addWidget(expense_section, 1)
        
        content_layout.addLayout(charts_row)
        
        # Quick stats section
        stats_section = QFrame()
        stats_section.setObjectName("dashboard-section")
        stats_section.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
            QFrame#stat-item {
                background: rgba(60, 60, 80, 0.3);
                border: 1px solid rgba(80, 80, 100, 0.3);
                border-radius: 8px;
            }
            QFrame#stat-item:hover {
                background: rgba(70, 70, 90, 0.4);
                border-color: rgba(100, 150, 255, 0.4);
            }
        """)
        stats_layout = QVBoxLayout(stats_section)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title with icon
        stats_header = QHBoxLayout()
        
        stats_icon = QLabel()
        from src.shared.icon_utils import load_themed_icon
        stats_icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_chart.svg"), size=(20, 20))
        stats_icon.setPixmap(stats_icon_pixmap)
        stats_header.addWidget(stats_icon)
        
        stats_title = QLabel("Quick Stats")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        stats_title.setFont(font)
        stats_header.addWidget(stats_title)
        stats_header.addStretch()
        
        stats_layout.addLayout(stats_header)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        from src.core.config import config
        currency_symbol = config.get('currency.symbol', '$')
        
        self.notes_stat = self.create_stat_item("Notes", "0", "feature_notes.svg")
        self.expenses_stat = self.create_stat_item("Expenses This Month", f"{currency_symbol}0", "feature_expenses.svg")
        self.events_week_stat = self.create_stat_item("Events This Week", "0", "icon_calendar.svg")
        self.habits_stat = self.create_stat_item("Active Habits", "0", "feature_habits.svg")
        
        stats_grid.addWidget(self.notes_stat, 0, 0)
        stats_grid.addWidget(self.expenses_stat, 0, 1)
        stats_grid.addWidget(self.events_week_stat, 1, 0)
        stats_grid.addWidget(self.habits_stat, 1, 1)
        
        stats_layout.addLayout(stats_grid)
        content_layout.addWidget(stats_section)
        
        # Recent activity section
        activity_section = QFrame()
        activity_section.setObjectName("dashboard-section")
        activity_section.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
        """)
        activity_layout = QVBoxLayout(activity_section)
        activity_layout.setSpacing(15)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title with icon
        activity_header = QHBoxLayout()
        
        activity_icon = QLabel()
        from src.shared.icon_utils import load_themed_icon
        activity_icon_pixmap = load_themed_icon(get_resource_path("assets/icons/icon_clock.svg"), size=(20, 20))
        activity_icon.setPixmap(activity_icon_pixmap)
        activity_header.addWidget(activity_icon)
        
        activity_title = QLabel("Recent Activity")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        activity_title.setFont(font)
        activity_header.addWidget(activity_title)
        activity_header.addStretch()
        
        activity_layout.addLayout(activity_header)
        
        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(8)
        activity_layout.addLayout(self.recent_container)
        
        content_layout.addWidget(activity_section)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Store initial values for animation
        self.initial_load = True
        
        # Load data with slight delay for animation effect
        QTimer.singleShot(100, self.load_data_with_animation)
    
    def update_welcome_message(self):
        """Update welcome message based on time of day"""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        self.welcome_label.setText(f"{greeting} • {datetime.now().strftime('%B %d, %Y')}")
    
    def create_stat_item(self, label: str, value: str, icon_path: str) -> QFrame:
        """Create a stat item widget with icon"""
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_themed_icon
        
        frame = QFrame()
        frame.setObjectName("stat-item")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{icon_path}"), size=(16, 16))
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)
        
        # Label
        label_widget = QLabel(label)
        font = QFont()
        font.setPointSize(10)
        label_widget.setFont(font)
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        # Value
        value_widget = QLabel(value)
        value_widget.setObjectName("stat-value")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        value_widget.setFont(font)
        layout.addWidget(value_widget)
        
        return frame
    
    def update_stat_item(self, frame: QFrame, value: str):
        """Update stat item value"""
        layout = frame.layout()
        if layout and layout.count() >= 4:
            value_widget = layout.itemAt(3).widget()
            if isinstance(value_widget, QLabel):
                value_widget.setText(value)
    
    def load_data_with_animation(self):
        """Load data and trigger animations"""
        from src.core.config import config
        
        # Reset all progress values to 0 BEFORE loading data
        if config.get('appearance.enable_animations', True) and self.initial_load:
            # Reset stat cards
            self.events_card._displayed_value = 0
            self.habits_card._displayed_value = 0
            self.notes_card._displayed_value = 0
            self.expenses_card._displayed_value = 0
            
            # Reset progress rings
            self.habits_total_ring._progress = 0
            self.habits_total_ring._target_progress = 0
            self.habits_today_ring._progress = 0
            self.habits_today_ring._target_progress = 0
            self.events_ring._progress = 0
            self.events_ring._target_progress = 0
            self.expenses_ring._progress = 0
            self.expenses_ring._target_progress = 0
            self.expense_chart.canvas._animation_progress = 0
            
            self.habits_total_ring.update()
            self.habits_today_ring.update()
            self.events_ring.update()
            self.expenses_ring.update()
            self.expense_chart.canvas.update()
        
        # Load data which will trigger animations
        self.load_data()
    
    def load_data(self):
        """Load data from database and update UI"""
        from src.models import Event, Habit, Note, Expense
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            
            # Update welcome message
            self.update_welcome_message()
            
            # Determine if we should animate (only on initial load or when animations enabled)
            from src.core.config import config
            should_animate = config.get('appearance.enable_animations', True) and self.initial_load
            self.initial_load = False
            
            # Count upcoming events (next 7 days)
            today = datetime.now().date()
            week_later = today + timedelta(days=7)
            upcoming_events = Event.select().where(
                (Event.start_date >= today) & (Event.start_date <= week_later)
            ).count()
            self.events_card.set_value(upcoming_events, animate=should_animate)
            
            # Count active habits
            active_habits = Habit.select().count()
            self.habits_card.set_value(active_habits, animate=should_animate)
            
            # Count notes
            note_count = Note.select().count()
            self.notes_card.set_value(note_count, animate=should_animate)
            
            # Calculate expenses this month
            first_day = datetime.now().replace(day=1).date()
            month_expenses = Expense.select().where(Expense.date >= first_day)
            total_expenses = float(sum(e.amount for e in month_expenses))
            
            # Format with currency symbol
            from src.shared.formatters import format_currency
            formatted_expenses = format_currency(total_expenses)
            self.expenses_card.set_value(formatted_expenses, animate=should_animate)
            
            # Calculate habit streak (average current streak / target days)
            from src.models.habit import HabitLog
            habits = Habit.select()
            if habits.count() > 0:
                total_streak_percent = 0
                today_success = 0
                today = datetime.now().date()
                
                for habit in habits:
                    is_bad_habit = habit.habit_type == "Bad"
                    
                    # Calculate current streak (limit to 365 days to prevent infinite loop)
                    current_streak = 0
                    check_date = today
                    max_days_to_check = min(365, habit.target_days * 2)  # Reasonable limit
                    days_checked = 0
                    
                    while days_checked < max_days_to_check:
                        # Don't check dates before habit was created
                        if check_date < habit.start_date:
                            break
                        
                        log = HabitLog.select().where(
                            (HabitLog.habit == habit) & (HabitLog.date == check_date)
                        ).first()
                        
                        # For good habits: streak continues if completed
                        # For bad habits: streak continues if NOT completed (avoided)
                        if is_bad_habit:
                            # Bad habit: check if NOT done (no log or not completed)
                            if not log or not log.completed:
                                current_streak += 1
                                check_date = check_date - timedelta(days=1)
                                days_checked += 1
                            else:
                                break  # Did the bad habit, streak broken
                        else:
                            # Good habit: check if done
                            if log and log.completed:
                                current_streak += 1
                                check_date = check_date - timedelta(days=1)
                                days_checked += 1
                            else:
                                break  # Didn't do the good habit, streak broken
                    
                    # Calculate percentage for this habit
                    streak_percent = (current_streak / habit.target_days * 100) if habit.target_days > 0 else 0
                    total_streak_percent += min(streak_percent, 100)
                    
                    # Check if successful today
                    today_log = HabitLog.select().where(
                        (HabitLog.habit == habit) & (HabitLog.date == today)
                    ).first()
                    
                    # For good habits: success = completed
                    # For bad habits: success = NOT completed (avoided)
                    if is_bad_habit:
                        if not today_log or not today_log.completed:
                            today_success += 1
                    else:
                        if today_log and today_log.completed:
                            today_success += 1
                
                # Set total habits progress (average streak)
                avg_streak = total_streak_percent / habits.count()
                self.habits_total_ring.set_progress(avg_streak, animate=should_animate)
                
                # Set today's success rate
                today_percent = (today_success / habits.count() * 100) if habits.count() > 0 else 0
                self.habits_today_ring.set_progress(today_percent, animate=should_animate)
            else:
                self.habits_total_ring.set_progress(0, animate=should_animate)
                self.habits_today_ring.set_progress(0, animate=should_animate)
            
            # Events this week progress
            events_week = Event.select().where(
                (Event.start_date >= today) & (Event.start_date <= week_later)
            ).count()
            # Show as percentage (up to 10 events = 100%)
            events_percent = min((events_week / 10 * 100), 100) if events_week > 0 else 0
            self.events_ring.set_progress(events_percent, animate=should_animate)
            
            # Budget usage (expenses vs a reasonable monthly budget estimate)
            # Using 50000 as default budget for percentage calculation
            budget_limit = 50000
            budget_percent = min((total_expenses / budget_limit * 100), 100) if total_expenses > 0 else 0
            self.expenses_ring.set_progress(budget_percent, animate=should_animate)
            
            # Load expense data for pie chart
            first_day = datetime.now().replace(day=1).date()
            month_expenses = Expense.select().where(Expense.date >= first_day)
            
            # Group by category
            category_totals = {}
            for expense in month_expenses:
                category = expense.category or "Other"
                category_totals[category] = category_totals.get(category, 0) + expense.amount
            
            # Convert to list and sort by amount
            expense_data = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            self.expense_chart.set_data(expense_data, animate=should_animate)
            
            # Update quick stats
            note_count = Note.select().count()
            self.update_stat_item(self.notes_stat, str(note_count))
            
            # Active habits
            active_habits = Habit.select().count()
            self.update_stat_item(self.habits_stat, str(active_habits))
            
            # Expenses this month
            from src.core.config import config
            currency_symbol = config.get('currency.symbol', '$')
            
            first_day = datetime.now().replace(day=1).date()
            month_expenses = Expense.select().where(Expense.date >= first_day)
            total_expenses = float(sum(e.amount for e in month_expenses))
            self.update_stat_item(self.expenses_stat, f"{currency_symbol}{total_expenses:.2f}")
            
            # Events this week
            events_week = Event.select().where(
                (Event.start_date >= today) & (Event.start_date <= week_later)
            ).count()
            self.update_stat_item(self.events_week_stat, str(events_week))
            
            # Load recent activity from logs
            self.load_recent_activity()
            
            db.close()
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def load_recent_activity(self):
        """Load and display recent activity from logs"""
        # Clear existing items
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            from src.core.activity_logger import activity_logger
            from src.core.config import config
            
            # Get activity mode from settings
            activity_mode = config.get('advanced.recent_activity_mode', 'standard')
            
            # If disabled, show message with link to settings
            if activity_mode == 'none':
                disabled_widget = QFrame()
                disabled_layout = QVBoxLayout(disabled_widget)
                disabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                disabled_label = QLabel("Recent Activity is disabled")
                disabled_label.setProperty("class", "secondary-text")
                disabled_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                disabled_layout.addWidget(disabled_label)
                
                enable_btn = QPushButton("Enable in Settings")
                enable_btn.setProperty("class", "secondary-button")
                enable_btn.clicked.connect(self.open_activity_settings)
                disabled_layout.addWidget(enable_btn, 0, Qt.AlignmentFlag.AlignCenter)
                
                self.recent_container.addWidget(disabled_widget)
                return
            
            # Get recent activities excluding Settings and System
            activities = activity_logger.get_recent_activities(
                mode=activity_mode,
                limit=5,
                exclude_features=['Settings', 'System']
            )
            
            if activities:
                for activity in activities:
                    # Map feature to icon file
                    icon_map = {
                        'Calendar': 'icon_calendar.svg',
                        'Expenses': 'feature_expenses.svg',
                        'Habits': 'feature_habits.svg',
                        'Notes': 'feature_notes.svg'
                    }
                    
                    icon_file = icon_map.get(activity['feature'], 'feature_dashboard.svg')
                    text = f"{activity['action']}"
                    if activity['details']:
                        text += f": {activity['details']}"
                    
                    item = self.create_activity_item(
                        icon_file,
                        text,
                        activity['timestamp']
                    )
                    self.recent_container.addWidget(item)
            else:
                no_activity = QLabel("No recent activity")
                no_activity.setProperty("class", "secondary-text")
                no_activity.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.recent_container.addWidget(no_activity)
        
        except Exception as e:
            print(f"Error loading recent activity: {e}")
    
    def open_activity_settings(self):
        """Open settings and navigate to advanced section"""
        try:
            # Emit signal to switch to settings
            from src.core.signals import signals
            signals.navigate_requested.emit('Settings')
            
            # TODO: Navigate to advanced section within settings
            # This would require the settings view to support direct section navigation
        except Exception as e:
            print(f"Error opening settings: {e}")
    
    def create_activity_item(self, icon_file: str, text: str, time: datetime) -> QWidget:
        """Create an activity item with SVG icon"""
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_themed_icon
        
        item_widget = QFrame()
        item_widget.setProperty("class", "activity-item")
        item_widget.setStyleSheet("""
            QFrame.activity-item {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                padding: 8px 12px;
            }
            QFrame.activity-item:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel()
        icon_pixmap = load_themed_icon(get_resource_path(f"assets/icons/{icon_file}"), size=(18, 18))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedWidth(24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text
        text_label = QLabel(text)
        font = QFont()
        font.setPointSize(10)
        text_label.setFont(font)
        text_label.setWordWrap(True)
        layout.addWidget(text_label, 1)
        
        # Time
        from src.shared.formatters import format_datetime
        time_label = QLabel(format_datetime(time))
        time_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        time_label.setFont(font)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(time_label)
        
        return item_widget
    
    def refresh(self):
        """Refresh view to apply config changes"""
        # Reload header icon with current theme
        from src.core.path_manager import get_resource_path
        from src.shared.icon_utils import load_accent_icon
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/feature_dashboard.svg"), size=(28, 28))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)
        
        # Mark as initial load to trigger animations
        self.initial_load = True
        
        # Reset widgets to 0 state before loading
        from src.core.config import config
        if config.get('appearance.enable_animations', True):
            # Reset stat cards
            self.events_card._displayed_value = 0
            self.habits_card._displayed_value = 0
            self.notes_card._displayed_value = 0
            self.expenses_card._displayed_value = 0
            
            # Reset progress rings
            self.habits_total_ring._progress = 0
            self.habits_total_ring._target_progress = 0
            self.habits_today_ring._progress = 0
            self.habits_today_ring._target_progress = 0
            self.events_ring._progress = 0
            self.events_ring._target_progress = 0
            self.expenses_ring._progress = 0
            self.expenses_ring._target_progress = 0
            self.expense_chart.canvas._animation_progress = 0
            
            self.habits_total_ring.update()
            self.habits_today_ring.update()
            self.events_ring.update()
            self.expenses_ring.update()
            self.expense_chart.canvas.update()
        
        self.load_data_with_animation()
    
    def showEvent(self, event):
        """Handle show event to trigger animations"""
        super().showEvent(event)
        # Trigger animations when dashboard becomes visible
        if hasattr(self, 'habits_total_ring'):
            from src.core.config import config
            
            # Immediately reset to 0 if animations are enabled
            if config.get('appearance.enable_animations', True):
                # Reset stat cards
                self.events_card._displayed_value = 0
                self.habits_card._displayed_value = 0
                self.notes_card._displayed_value = 0
                self.expenses_card._displayed_value = 0
                
                # Reset progress rings
                self.habits_total_ring._progress = 0
                self.habits_total_ring._target_progress = 0
                self.habits_today_ring._progress = 0
                self.habits_today_ring._target_progress = 0
                self.events_ring._progress = 0
                self.events_ring._target_progress = 0
                self.expenses_ring._progress = 0
                self.expenses_ring._target_progress = 0
                self.expense_chart.canvas._animation_progress = 0
                
                self.habits_total_ring.update()
                self.habits_today_ring.update()
                self.events_ring.update()
                self.expenses_ring.update()
                self.expense_chart.canvas.update()
            
            # Mark as initial load to trigger animations
            self.initial_load = True
            # Small delay to load data and start animations
            QTimer.singleShot(50, self.load_data_with_animation)
