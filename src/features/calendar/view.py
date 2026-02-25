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
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(40, 40)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.clicked.connect(self.prev_month)
        nav_layout.addWidget(prev_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        self.month_label = QLabel()
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.month_label.setFont(font)
        self.month_label.setMinimumWidth(250)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.month_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        next_btn = QPushButton("▶")
        next_btn.setFixedSize(40, 40)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(next_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        today_btn = QPushButton("Today")
        today_btn.setMinimumWidth(80)
        today_btn.setFixedHeight(40)
        today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        today_btn.clicked.connect(self.go_to_today)
        nav_layout.addWidget(today_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        header.addLayout(nav_layout)
        header.addStretch()
        
        # Add event button
        add_btn = QPushButton("+ Add Event")
        add_btn.setMinimumWidth(120)
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.on_add_event)
        header.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        layout.addLayout(header)
        
        # Main content: calendar grid + events list
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Calendar grid (left side) - styled like dashboard sections
        self.calendar_container = QFrame()
        self.calendar_container.setObjectName("dashboard-section")
        self.calendar_container.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
        """)
        calendar_layout = QVBoxLayout(self.calendar_container)
        calendar_layout.setContentsMargins(20, 20, 20, 20)
        calendar_layout.setSpacing(10)
        
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(8)
        self.calendar_grid.setHorizontalSpacing(8)
        self.calendar_grid.setVerticalSpacing(8)
        
        # Make all columns equal width
        for col in range(7):
            self.calendar_grid.setColumnStretch(col, 1)
        
        # Make all rows equal height (except header)
        for row in range(1, 7):  # Skip row 0 (header)
            self.calendar_grid.setRowStretch(row, 1)
        
        calendar_layout.addLayout(self.calendar_grid)
        
        content.addWidget(self.calendar_container, 3)
        
        # Events list (right side) - styled like dashboard sections
        events_panel = QFrame()
        events_panel.setObjectName("dashboard-section")
        events_panel.setStyleSheet("""
            QFrame#dashboard-section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 90, 0.25),
                    stop:1 rgba(50, 50, 70, 0.15));
                border: 1px solid rgba(100, 100, 120, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
        """)
        events_panel.setMinimumWidth(340)
        events_panel.setMaximumWidth(360)
        events_layout = QVBoxLayout(events_panel)
        events_layout.setContentsMargins(15, 20, 15, 20)
        events_layout.setSpacing(15)
        
        # Tab buttons
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(8)
        
        self.upcoming_tab = QPushButton("Upcoming")
        self.upcoming_tab.setCheckable(True)
        self.upcoming_tab.setChecked(True)
        self.upcoming_tab.setMinimumHeight(36)
        self.upcoming_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upcoming_tab.clicked.connect(lambda: self.switch_events_view("upcoming"))
        tabs_layout.addWidget(self.upcoming_tab)
        
        self.recent_tab = QPushButton("Recent")
        self.recent_tab.setCheckable(True)
        self.recent_tab.setMinimumHeight(36)
        self.recent_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.recent_tab.clicked.connect(lambda: self.switch_events_view("recent"))
        tabs_layout.addWidget(self.recent_tab)
        
        events_layout.addLayout(tabs_layout)
        
        # Events scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.events_list = QWidget()
        self.events_list_layout = QVBoxLayout(self.events_list)
        self.events_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.events_list_layout.setSpacing(12)
        self.events_list_layout.setContentsMargins(2, 2, 2, 2)
        
        scroll.setWidget(self.events_list)
        events_layout.addWidget(scroll)
        
        content.addWidget(events_panel, 1)
        
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
            font.setPointSize(10)
            header.setFont(font)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setMinimumHeight(30)
            header.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    padding: 5px;
                }
            """)
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
                    # Empty cell with same styling
                    empty = QFrame()
                    empty.setObjectName("calendar-day-cell-empty")
                    empty.setStyleSheet("""
                        QFrame#calendar-day-cell-empty {
                            background: rgba(40, 40, 60, 0.2);
                            border: 1px solid rgba(60, 60, 80, 0.2);
                            border-radius: 8px;
                        }
                    """)
                    self.calendar_grid.addWidget(empty, week_num + 1, day_num)
                    continue
                
                date = datetime(self.current_date.year, self.current_date.month, day).date()
                is_today = date == today
                
                # Day cell (clickable)
                day_cell = QFrame()
                day_cell.setObjectName("calendar-day-cell")
                day_cell.setCursor(Qt.CursorShape.PointingHandCursor)
                day_cell.mousePressEvent = lambda e, d=date: self.on_date_clicked(d)
                
                # Style the day cell
                if is_today:
                    day_cell.setStyleSheet("""
                        QFrame#calendar-day-cell {
                            background: rgba(80, 80, 100, 0.4);
                            border: 2px solid rgba(137, 180, 250, 0.8);
                            border-radius: 8px;
                        }
                        QFrame#calendar-day-cell:hover {
                            background: rgba(90, 90, 110, 0.5);
                            border-color: rgba(137, 180, 250, 1.0);
                        }
                    """)
                else:
                    day_cell.setStyleSheet("""
                        QFrame#calendar-day-cell {
                            background: rgba(60, 60, 80, 0.3);
                            border: 1px solid rgba(80, 80, 100, 0.3);
                            border-radius: 8px;
                        }
                        QFrame#calendar-day-cell:hover {
                            background: rgba(70, 70, 90, 0.4);
                            border-color: rgba(100, 150, 255, 0.4);
                        }
                    """)
                
                cell_layout = QVBoxLayout(day_cell)
                cell_layout.setContentsMargins(8, 8, 8, 8)
                cell_layout.setSpacing(4)
                
                # Day number
                day_label = QLabel(str(day))
                font = QFont()
                font.setPointSize(12)
                font.setBold(is_today)
                day_label.setFont(font)
                if is_today:
                    day_label.setStyleSheet("color: rgba(137, 180, 250, 1.0);")
                cell_layout.addWidget(day_label)
                
                # Event indicators (max 3, with event names)
                if date in events_by_date:
                    for event in events_by_date[date][:3]:
                        # Event container with color bar and name
                        event_container = QHBoxLayout()
                        event_container.setSpacing(4)
                        event_container.setContentsMargins(0, 0, 0, 0)
                        
                        # Color indicator bar
                        event_indicator = QFrame()
                        event_indicator.setFixedSize(3, 14)
                        event_indicator.setStyleSheet(f"""
                            QFrame {{
                                background-color: {event.color};
                                border-radius: 1px;
                            }}
                        """)
                        event_container.addWidget(event_indicator)
                        
                        # Event name (truncated)
                        event_name = QLabel(self.truncate_text(event.title, 12))
                        event_name.setStyleSheet(f"font-size: 8pt; color: {event.color};")
                        event_name.setWordWrap(False)
                        event_name.setSizePolicy(
                            event_name.sizePolicy().Policy.Expanding,
                            event_name.sizePolicy().Policy.Fixed
                        )
                        event_container.addWidget(event_name, 1)
                        
                        cell_layout.addLayout(event_container)
                    
                    if len(events_by_date[date]) > 3:
                        more_label = QLabel(f"+{len(events_by_date[date]) - 3} more")
                        more_label.setProperty("class", "small-text")
                        more_label.setStyleSheet("font-size: 7pt; color: rgba(255, 255, 255, 0.5);")
                        more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        cell_layout.addWidget(more_label)
                
                cell_layout.addStretch()
                
                self.calendar_grid.addWidget(day_cell, week_num + 1, day_num)
        
        # Load events list
        self.load_events_list()
    
    def load_events_list(self):
        """Load events list based on current view"""
        # Clear existing
        for i in reversed(range(self.events_list_layout.count())):
            item = self.events_list_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.events_list_layout.removeItem(item)
        
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
        else:
            # Create event items
            from src.features.calendar.widgets.event_item import EventItem
            for event in events:
                item = EventItem(event, self)
                item.event_updated.connect(self.on_event_updated)
                item.event_deleted.connect(self.on_event_deleted)
                self.events_list_layout.addWidget(item)
        
        # Add stretch to push items to top
        self.events_list_layout.addStretch()
        
        # Force layout update
        self.events_list.adjustSize()
    
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
