"""
Calendar View
Main calendar interface with month grid and events list
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
import calendar

from src.features.calendar.controller import CalendarController
from src.features.calendar.widgets.event_dialog import EventDialog
from src.core.config import config


class CalendarView(QWidget):
    """Calendar view with month grid and events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = CalendarController()
        self.current_date = datetime.now()
        self.events_view = "upcoming"  # "upcoming" or "recent"
        self.setup_ui()
        self.load_calendar()
    
    def setup_ui(self):
        """Setup calendar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with navigation
        header = QHBoxLayout()
        
        # Month navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        prev_btn = QPushButton("◀")
        prev_btn.clicked.connect(self.prev_month)
        nav_layout.addWidget(prev_btn)
        
        self.month_label = QLabel()
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.month_label.setFont(font)
        self.month_label.setMinimumWidth(200)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.month_label)
        
        next_btn = QPushButton("▶")
        next_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(next_btn)
        
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_to_today)
        nav_layout.addWidget(today_btn)
        
        header.addLayout(nav_layout)
        header.addStretch()
        
        # Add event button
        add_btn = QPushButton("+ Add Event")
        add_btn.clicked.connect(self.on_add_event)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Main content: calendar grid + events list
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Calendar grid (left side)
        self.calendar_container = QFrame()
        self.calendar_container.setObjectName("settings-section")
        calendar_layout = QVBoxLayout(self.calendar_container)
        calendar_layout.setContentsMargins(15, 15, 15, 15)
        
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(5)
        calendar_layout.addLayout(self.calendar_grid)
        
        content.addWidget(self.calendar_container, 2)
        
        # Events list (right side)
        events_panel = QFrame()
        events_panel.setObjectName("settings-section")
        events_panel.setMinimumWidth(300)
        events_panel.setMaximumWidth(400)
        events_layout = QVBoxLayout(events_panel)
        events_layout.setContentsMargins(15, 15, 15, 15)
        events_layout.setSpacing(10)
        
        # Tab buttons
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(5)
        
        self.upcoming_tab = QPushButton("Upcoming")
        self.upcoming_tab.setCheckable(True)
        self.upcoming_tab.setChecked(True)
        self.upcoming_tab.clicked.connect(lambda: self.switch_events_view("upcoming"))
        tabs_layout.addWidget(self.upcoming_tab)
        
        self.recent_tab = QPushButton("Recent")
        self.recent_tab.setCheckable(True)
        self.recent_tab.clicked.connect(lambda: self.switch_events_view("recent"))
        tabs_layout.addWidget(self.recent_tab)
        
        events_layout.addLayout(tabs_layout)
        
        # Events scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.events_list = QWidget()
        self.events_list_layout = QVBoxLayout(self.events_list)
        self.events_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.events_list_layout.setSpacing(10)
        
        scroll.setWidget(self.events_list)
        events_layout.addWidget(scroll)
        
        content.addWidget(events_panel)
        
        layout.addLayout(content, 1)
        
        self.setLayout(layout)
    
    def load_calendar(self):
        """Load calendar for current month"""
        # Clear existing calendar
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Update month label
        month_name = self.current_date.strftime("%B")
        self.month_label.setText(f"{month_name} {self.current_date.year}")
        
        # Get first day of week setting
        first_day = config.get('locale.week_starts_on', 'Monday')
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if first_day == "Sunday":
            weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        
        # Weekday headers
        for i, day in enumerate(weekdays):
            header = QLabel(day)
            font = QFont()
            font.setBold(True)
            header.setFont(font)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_grid.addWidget(header, 0, i)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Adjust for week start day
        if first_day == "Sunday":
            # Rotate each week to start with Sunday
            cal = [[week[-1]] + week[:-1] if week[-1] != 0 else [0] + week[:-1] for week in cal]
        
        # Get events for this month
        events = self.controller.get_events_for_month(
            self.current_date.year,
            self.current_date.month
        )
        
        # Group events by date
        events_by_date = {}
        for event in events:
            date_key = event.start_date.date()
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)
        
        # Create day cells
        today = datetime.now().date()
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    empty = QLabel("")
                    self.calendar_grid.addWidget(empty, week_num + 1, day_num)
                    continue
                
                date = datetime(self.current_date.year, self.current_date.month, day).date()
                is_today = date == today
                
                # Day cell (clickable)
                day_cell = QFrame()
                day_cell.setObjectName("task-item")
                day_cell.setCursor(Qt.CursorShape.PointingHandCursor)
                day_cell.mousePressEvent = lambda e, d=date: self.on_date_clicked(d)
                if is_today:
                    day_cell.setStyleSheet("QFrame#task-item { border: 2px solid; }")
                
                cell_layout = QVBoxLayout(day_cell)
                cell_layout.setContentsMargins(5, 5, 5, 5)
                cell_layout.setSpacing(2)
                
                # Day number
                day_label = QLabel(str(day))
                font = QFont()
                font.setBold(is_today)
                day_label.setFont(font)
                cell_layout.addWidget(day_label)
                
                # Event indicators (max 3)
                if date in events_by_date:
                    for event in events_by_date[date][:3]:
                        event_label = QLabel(self.truncate_text(event.title, 12))
                        event_label.setProperty("class", "small-text")
                        event_label.setStyleSheet(f"color: {event.color};")
                        cell_layout.addWidget(event_label)
                    
                    if len(events_by_date[date]) > 3:
                        more_label = QLabel(f"+{len(events_by_date[date]) - 3} more")
                        more_label.setProperty("class", "small-text")
                        cell_layout.addWidget(more_label)
                
                cell_layout.addStretch()
                
                self.calendar_grid.addWidget(day_cell, week_num + 1, day_num)
        
        # Load events list
        self.load_events_list()
    
    def load_events_list(self):
        """Load events list based on current view"""
        # Clear existing
        for i in reversed(range(self.events_list_layout.count())):
            widget = self.events_list_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get events
        if self.events_view == "upcoming":
            events = self.controller.get_upcoming_events()
        else:
            events = self.controller.get_recent_events()
        
        if not events:
            no_events = QLabel("No events" if self.events_view == "upcoming" else "No recent events")
            no_events.setProperty("class", "secondary-text")
            no_events.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_list_layout.addWidget(no_events)
            return
        
        # Create event items
        from src.features.calendar.widgets.event_item import EventItem
        for event in events:
            item = EventItem(event, self)
            item.event_updated.connect(self.on_event_updated)
            item.event_deleted.connect(self.on_event_deleted)
            self.events_list_layout.addWidget(item)
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.load_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.load_calendar()
    
    def go_to_today(self):
        """Go to current month"""
        self.current_date = datetime.now()
        self.load_calendar()
    
    def switch_events_view(self, view: str):
        """Switch between upcoming and recent events"""
        self.events_view = view
        self.upcoming_tab.setChecked(view == "upcoming")
        self.recent_tab.setChecked(view == "recent")
        self.load_events_list()
    
    def on_add_event(self):
        """Handle add event button"""
        dialog = EventDialog(self)
        if dialog.exec():
            event_data = dialog.get_event_data()
            self.controller.create_event(event_data)
            self.load_calendar()
    
    def on_event_updated(self):
        """Handle event update"""
        self.load_calendar()
    
    def on_event_deleted(self):
        """Handle event deletion"""
        self.load_calendar()
    
    def on_date_clicked(self, date):
        """Handle date cell click - create new event"""
        from datetime import datetime
        dialog = EventDialog(self)
        # Pre-fill with clicked date
        dialog.date_input.setDate(QDate(date.year, date.month, date.day))
        if dialog.exec():
            event_data = dialog.get_event_data()
            self.controller.create_event(event_data)
            self.load_calendar()
    
    def navigate_to_date(self, date):
        """Navigate calendar to show a specific date"""
        self.current_date = datetime(date.year, date.month, 1)
        self.load_calendar()
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
