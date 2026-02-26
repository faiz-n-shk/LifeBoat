"""
Dashboard View
Main overview page with charts and statistics
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
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
        header = QLabel("📊 Dashboard")
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
        self.tasks_card = StatCard("Active Tasks", "📝")
        self.todos_card = StatCard("Active Todos", "✓")
        self.events_card = StatCard("Upcoming Events", "📅")
        self.goals_card = StatCard("Active Goals", "🎯")
        
        cards_layout.addWidget(self.tasks_card)
        cards_layout.addWidget(self.todos_card)
        cards_layout.addWidget(self.events_card)
        cards_layout.addWidget(self.goals_card)
        
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
        
        section_title = QLabel("📈 Progress Overview")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        section_title.setFont(font)
        progress_layout.addWidget(section_title)
        
        # Progress rings in 2x3 grid
        rings_grid = QGridLayout()
        rings_grid.setSpacing(15)
        rings_grid.setHorizontalSpacing(20)
        
        # Top row: Tasks, Todo Total, Todo Today
        self.tasks_ring = ProgressRing("Tasks Completed")
        self.todo_total_ring = ProgressRing("Todo Progress")
        self.todo_today_ring = ProgressRing("Todo Today")
        
        rings_grid.addWidget(self.tasks_ring, 0, 0)
        rings_grid.addWidget(self.todo_total_ring, 0, 1)
        rings_grid.addWidget(self.todo_today_ring, 0, 2)
        
        # Bottom row: Goals, Habits Total, Habits Today
        self.goals_ring = ProgressRing("Goals Progress")
        self.habits_total_ring = ProgressRing("Habits Streak")
        self.habits_today_ring = ProgressRing("Habits Today")
        
        rings_grid.addWidget(self.goals_ring, 1, 0)
        rings_grid.addWidget(self.habits_total_ring, 1, 1)
        rings_grid.addWidget(self.habits_today_ring, 1, 2)
        
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
        
        expense_title = QLabel("💰 Expenses by Category")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        expense_title.setFont(font)
        expense_layout.addWidget(expense_title)
        
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
        
        stats_title = QLabel("📊 Quick Stats")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        stats_title.setFont(font)
        stats_layout.addWidget(stats_title)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        from src.core.config import config
        currency_symbol = config.get('currency.symbol', '$')
        
        self.notes_stat = self.create_stat_item("📝 Notes", "0")
        self.overdue_stat = self.create_stat_item("⚠️ Overdue Todos", "0")
        self.expenses_stat = self.create_stat_item("💰 Expenses This Month", f"{currency_symbol}0")
        self.events_week_stat = self.create_stat_item("📅 Events This Week", "0")
        
        stats_grid.addWidget(self.notes_stat, 0, 0)
        stats_grid.addWidget(self.overdue_stat, 0, 1)
        stats_grid.addWidget(self.expenses_stat, 1, 0)
        stats_grid.addWidget(self.events_week_stat, 1, 1)
        
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
        
        activity_title = QLabel("🕐 Recent Activity")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        activity_title.setFont(font)
        activity_layout.addWidget(activity_title)
        
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
    
    def create_stat_item(self, label: str, value: str) -> QFrame:
        """Create a stat item widget"""
        frame = QFrame()
        frame.setObjectName("stat-item")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        
        label_widget = QLabel(label)
        font = QFont()
        font.setPointSize(10)
        label_widget.setFont(font)
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
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
        if layout and layout.count() >= 2:
            value_widget = layout.itemAt(2).widget()
            if isinstance(value_widget, QLabel):
                value_widget.setText(value)
    
    def load_data_with_animation(self):
        """Load data and trigger animations"""
        from src.core.config import config
        
        # Reset all progress values to 0 BEFORE loading data
        if config.get('appearance.enable_animations', True) and self.initial_load:
            self.tasks_ring._progress = 0
            self.tasks_ring._target_progress = 0
            self.goals_ring._progress = 0
            self.goals_ring._target_progress = 0
            self.habits_total_ring._progress = 0
            self.habits_total_ring._target_progress = 0
            self.habits_today_ring._progress = 0
            self.habits_today_ring._target_progress = 0
            self.todo_total_ring._progress = 0
            self.todo_total_ring._target_progress = 0
            self.todo_today_ring._progress = 0
            self.todo_today_ring._target_progress = 0
            self.expense_chart.canvas._animation_progress = 0
            
            self.tasks_ring.update()
            self.goals_ring.update()
            self.habits_total_ring.update()
            self.habits_today_ring.update()
            self.todo_total_ring.update()
            self.todo_today_ring.update()
            self.expense_chart.canvas.update()
        
        # Load data which will trigger animations
        self.load_data()
    
    def load_data(self):
        """Load data from database and update UI"""
        from src.models import Task, Event, Goal, Habit, Note, Expense
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            
            # Update welcome message
            self.update_welcome_message()
            
            # Determine if we should animate (only on initial load or when animations enabled)
            from src.core.config import config
            should_animate = config.get('appearance.enable_animations', True) and self.initial_load
            self.initial_load = False
            
            # Count active tasks
            active_tasks = Task.select().where(Task.completed == False).count()
            self.tasks_card.set_value(active_tasks, animate=should_animate)
            
            # Count active todos
            from src.models.todo import Todo
            active_todos = Todo.select().where(Todo.completed == False).count()
            self.todos_card.set_value(active_todos, animate=should_animate)
            
            # Count upcoming events (next 7 days)
            today = datetime.now().date()
            week_later = today + timedelta(days=7)
            upcoming_events = Event.select().where(
                (Event.start_date >= today) & (Event.start_date <= week_later)
            ).count()
            self.events_card.set_value(upcoming_events, animate=should_animate)
            
            # Count active goals
            active_goals = Goal.select().where(Goal.completed == False).count()
            self.goals_card.set_value(active_goals, animate=should_animate)
            
            # Calculate task completion rate
            total_tasks = Task.select().count()
            completed_tasks = Task.select().where(Task.completed == True).count()
            task_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            self.tasks_ring.set_progress(task_completion, animate=should_animate)
            
            # Calculate goal progress (average of all goals)
            goals = Goal.select().where(Goal.completed == False)
            if goals.count() > 0:
                avg_progress = sum(g.progress for g in goals) / goals.count()
                self.goals_ring.set_progress(avg_progress, animate=should_animate)
            else:
                self.goals_ring.set_progress(0, animate=should_animate)
            
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
            
            # Todo rings
            from src.models.todo import Todo
            total_todos = Todo.select().count()
            active_todos = Todo.select().where(Todo.completed == False).count()
            completed_todos = Todo.select().where(Todo.completed == True).count()
            today_todos = Todo.select().where(
                (Todo.completed == False) & 
                (Todo.due_date == today)
            ).count()
            
            # Total progress (completed / total)
            if total_todos > 0:
                total_progress = (completed_todos / total_todos * 100)
                self.todo_total_ring.set_progress(total_progress, animate=should_animate)
            else:
                self.todo_total_ring.set_progress(0, animate=should_animate)
            
            # Today progress (completed today / due today)
            today_total = Todo.select().where(Todo.due_date == today).count()
            today_completed = Todo.select().where(
                (Todo.completed == True) & 
                (Todo.due_date == today)
            ).count()
            
            if today_total > 0:
                today_progress = (today_completed / today_total * 100)
                self.todo_today_ring.set_progress(today_progress, animate=should_animate)
            else:
                self.todo_today_ring.set_progress(0, animate=should_animate)
            
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
            
            # Overdue todos
            overdue_todos = Todo.select().where(
                (Todo.completed == False) & 
                (Todo.due_date < today)
            ).count()
            self.update_stat_item(self.overdue_stat, str(overdue_todos))
            
            # Expenses this month
            from src.core.config import config
            currency_symbol = config.get('currency.symbol', '$')
            
            first_day = datetime.now().replace(day=1).date()
            month_expenses = Expense.select().where(Expense.date >= first_day)
            total_expenses = sum(e.amount for e in month_expenses)
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
                    # Map feature to icon
                    icon_map = {
                        'Tasks': '✓',
                        'Todos': '✓',
                        'Calendar': '📅',
                        'Expenses': '💰',
                        'Goals': '🎯',
                        'Habits': '🔄',
                        'Notes': '📝'
                    }
                    
                    icon = icon_map.get(activity['feature'], '•')
                    text = f"{activity['action']}"
                    if activity['details']:
                        text += f": {activity['details']}"
                    
                    item = self.create_activity_item(
                        icon,
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
    
    def create_activity_item(self, icon: str, text: str, time: datetime) -> QWidget:
        """Create an activity item"""
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
        icon_label = QLabel(icon)
        font = QFont()
        font.setPointSize(14)
        icon_label.setFont(font)
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
        # Mark as initial load to trigger animations
        self.initial_load = True
        
        # Reset widgets to 0 state before loading
        from src.core.config import config
        if config.get('appearance.enable_animations', True):
            self.tasks_ring._progress = 0
            self.tasks_ring._target_progress = 0
            self.goals_ring._progress = 0
            self.goals_ring._target_progress = 0
            self.habits_total_ring._progress = 0
            self.habits_total_ring._target_progress = 0
            self.habits_today_ring._progress = 0
            self.habits_today_ring._target_progress = 0
            self.todo_total_ring._progress = 0
            self.todo_total_ring._target_progress = 0
            self.todo_today_ring._progress = 0
            self.todo_today_ring._target_progress = 0
            self.expense_chart.canvas._animation_progress = 0
            
            self.tasks_ring.update()
            self.goals_ring.update()
            self.habits_total_ring.update()
            self.habits_today_ring.update()
            self.todo_total_ring.update()
            self.todo_today_ring.update()
            self.expense_chart.canvas.update()
        
        self.load_data_with_animation()
    
    def showEvent(self, event):
        """Handle show event to trigger animations"""
        super().showEvent(event)
        # Trigger animations when dashboard becomes visible
        if hasattr(self, 'tasks_ring'):
            from src.core.config import config
            
            # Immediately reset to 0 if animations are enabled
            if config.get('appearance.enable_animations', True):
                self.tasks_ring._progress = 0
                self.tasks_ring._target_progress = 0
                self.goals_ring._progress = 0
                self.goals_ring._target_progress = 0
                self.habits_total_ring._progress = 0
                self.habits_total_ring._target_progress = 0
                self.habits_today_ring._progress = 0
                self.habits_today_ring._target_progress = 0
                self.todo_total_ring._progress = 0
                self.todo_total_ring._target_progress = 0
                self.todo_today_ring._progress = 0
                self.todo_today_ring._target_progress = 0
                self.expense_chart.canvas._animation_progress = 0
                
                self.tasks_ring.update()
                self.goals_ring.update()
                self.habits_total_ring.update()
                self.habits_today_ring.update()
                self.todo_total_ring.update()
                self.todo_today_ring.update()
                self.expense_chart.canvas.update()
            
            # Mark as initial load to trigger animations
            self.initial_load = True
            # Small delay to load data and start animations
            QTimer.singleShot(50, self.load_data_with_animation)
