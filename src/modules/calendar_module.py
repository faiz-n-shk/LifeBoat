"""
Lifeboat - Calendar Module
Calendar view with events management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, ThemedComboBox
from src.ui.pickers import DatePicker, TimePicker
from src.core.theme_manager import theme_manager
from src.core.database import Event, db
from datetime import datetime, timedelta
import calendar
from src.core import config
from src.utils import helpers as utils


class CalendarModule(ThemedFrame):
    """Calendar module for events"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.current_date = datetime.now()
        self.selected_date = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_calendar()
    
    def setup_ui(self):
        """Setup calendar UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        header.grid_columnconfigure(1, weight=1)
        
        # Navigation
        nav_frame = ThemedFrame(header, color_key="bg_primary")
        nav_frame.grid(row=0, column=0, sticky="w")
        
        ThemedButton(
            nav_frame,
            text="◀",
            width=40,
            command=self.prev_month
        ).pack(side="left", padx=2)
        
        self.month_label = ThemedLabel(
            nav_frame,
            text="",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold"),
            width=200
        )
        self.month_label.pack(side="left", padx=10)
        
        ThemedButton(
            nav_frame,
            text="▶",
            width=40,
            command=self.next_month
        ).pack(side="left", padx=2)
        
        ThemedButton(
            nav_frame,
            text="Today",
            width=80,
            command=self.go_to_today
        ).pack(side="left", padx=10)
        
        # Add event button
        ThemedButton(
            header,
            text="+ Add Event",
            button_style="accent",
            command=self.show_add_event_dialog
        ).grid(row=0, column=2, sticky="e")
        
        # Calendar grid (left side)
        self.calendar_frame = ThemedFrame(self, color_key="bg_primary")
        self.calendar_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(7):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="row")
        
        # Events list (right side)
        events_panel = ThemedFrame(self, color_key="bg_secondary", corner_radius=10)
        events_panel.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=(0, 20))
        events_panel.grid_columnconfigure(0, weight=1)
        events_panel.grid_rowconfigure(1, weight=1)
        
        # Tab buttons
        tabs_frame = ThemedFrame(events_panel, color_key="bg_secondary")
        tabs_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        tabs_frame.grid_columnconfigure(0, weight=1)
        tabs_frame.grid_columnconfigure(1, weight=1)
        
        self.events_view = "upcoming"  # Default view
        
        self.upcoming_tab = ThemedButton(
            tabs_frame,
            text="Upcoming",
            height=35,
            command=lambda: self.switch_events_view("upcoming"),
            button_style="accent"
        )
        self.upcoming_tab.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.recent_tab = ThemedButton(
            tabs_frame,
            text="Recent",
            height=35,
            command=lambda: self.switch_events_view("recent")
        )
        self.recent_tab.grid(row=0, column=1, sticky="ew", padx=(3, 0))
        
        self.events_list = ctk.CTkScrollableFrame(
            events_panel,
            fg_color=theme_manager.get_color("bg_secondary"),
            width=300
        )
        self.events_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.events_list.grid_columnconfigure(0, weight=1)
    
    def load_calendar(self):
        """Load calendar for current month"""
        # Clear existing
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update month label
        month_name = utils.get_month_name(self.current_date.month)
        self.month_label.configure(text=f"{month_name} {self.current_date.year}")
        
        # Weekday headers
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            header = ThemedLabel(
                self.calendar_frame,
                text=day,
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
            )
            header.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
        
        # Get calendar data
        cal = utils.get_month_calendar(self.current_date.year, self.current_date.month)
        
        # Get events for this month
        month_start = self.current_date.replace(day=1)
        if self.current_date.month == 12:
            month_end = self.current_date.replace(year=self.current_date.year + 1, month=1, day=1)
        else:
            month_end = self.current_date.replace(month=self.current_date.month + 1, day=1)
        
        events = Event.select().where(
            (Event.start_date >= month_start) &
            (Event.start_date < month_end)
        )
        
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
                    continue
                
                date = datetime(self.current_date.year, self.current_date.month, day).date()
                is_today = date == today
                
                day_frame = ThemedFrame(
                    self.calendar_frame,
                    color_key="bg_tertiary" if is_today else "bg_secondary",
                    corner_radius=5
                )
                day_frame.grid(row=week_num + 1, column=day_num, padx=2, pady=2, sticky="nsew")
                day_frame.grid_columnconfigure(0, weight=1)
                
                # Day number
                day_label = ThemedLabel(
                    day_frame,
                    text=str(day),
                    font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold" if is_today else "normal")
                )
                day_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
                
                # Events for this day
                if date in events_by_date:
                    for i, event in enumerate(events_by_date[date][:3]):  # Show max 3 events
                        event_label = ThemedLabel(
                            day_frame,
                            text=utils.truncate_text(event.title, 15),
                            font=(config.FONT_FAMILY, 9),
                            color_key="fg_secondary"
                        )
                        event_label.grid(row=i + 1, column=0, padx=5, pady=2, sticky="w")
                    
                    if len(events_by_date[date]) > 3:
                        more_label = ThemedLabel(
                            day_frame,
                            text=f"+{len(events_by_date[date]) - 3} more",
                            font=(config.FONT_FAMILY, 8),
                            color_key="fg_secondary"
                        )
                        more_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")
        
        # Load events list
        self.load_events_list()
    
    def load_events_list(self):
        """Load events list based on current view"""
        for widget in self.events_list.winfo_children():
            widget.destroy()
        
        # Get events based on view
        today = datetime.now()
        
        if self.events_view == "upcoming":
            # Upcoming and current events
            events = Event.select().where(
                Event.start_date >= today
            ).order_by(Event.start_date).limit(20)
            empty_message = "No upcoming events"
        else:
            # Recent events (past)
            events = Event.select().where(
                Event.start_date < today
            ).order_by(Event.start_date.desc()).limit(20)
            empty_message = "No recent events"
        
        if not events:
            no_events = ThemedLabel(
                self.events_list,
                text=empty_message,
                color_key="fg_secondary"
            )
            no_events.pack(pady=20)
            return
        
        for event in events:
            event_frame = ThemedFrame(self.events_list, color_key="bg_tertiary", corner_radius=8)
            event_frame.pack(fill="x", pady=5, padx=5)
            event_frame.grid_columnconfigure(0, weight=1)
            
            # Make frame clickable to navigate to event date
            event_frame.bind("<Button-1>", lambda e, evt=event: self.navigate_to_event(evt))
            
            # Title
            title_label = ThemedLabel(
                event_frame,
                text=event.title,
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
            )
            title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
            title_label.bind("<Button-1>", lambda e, evt=event: self.navigate_to_event(evt))
            
            # Date/Time
            date_label = ThemedLabel(
                event_frame,
                text=utils.format_datetime(event.start_date),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary"
            )
            date_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
            date_label.bind("<Button-1>", lambda e, evt=event: self.navigate_to_event(evt))
            
            # Description
            if event.description:
                desc_label = ThemedLabel(
                    event_frame,
                    text=utils.truncate_text(event.description, 100),
                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                    color_key="fg_secondary",
                    wraplength=250
                )
                desc_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
                desc_label.bind("<Button-1>", lambda e, evt=event: self.navigate_to_event(evt))
            
            # Location
            row_num = 3 if event.description else 2
            if event.location:
                loc_label = ThemedLabel(
                    event_frame,
                    text=f"📍 {event.location}",
                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                    color_key="fg_secondary"
                )
                loc_label.grid(row=row_num, column=0, sticky="w", padx=10, pady=(0, 5))
                loc_label.bind("<Button-1>", lambda e, evt=event: self.navigate_to_event(evt))
                row_num += 1
            
            # Actions
            actions_frame = ThemedFrame(event_frame, color_key="bg_tertiary")
            actions_frame.grid(row=row_num, column=0, sticky="ew", padx=10, pady=(5, 10))
            
            ThemedButton(
                actions_frame,
                text="Edit",
                width=60,
                command=lambda e=event: self.edit_event(e)
            ).pack(side="left", padx=2)
            
            ThemedButton(
                actions_frame,
                text="Delete",
                button_style="danger",
                width=60,
                command=lambda e=event: self.delete_event(e)
            ).pack(side="left", padx=2)
    
    def edit_event(self, event):
        """Edit an event"""
        self.show_add_event_dialog(event)
    
    def delete_event(self, event):
        """Delete an event"""
        event.delete_instance()
        self.load_calendar()
    
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
    
    def go_to_date(self, date):
        """Go to specific date"""
        # Convert to datetime if it's a date object
        if hasattr(date, 'year') and hasattr(date, 'month'):
            self.current_date = datetime(date.year, date.month, 1)
        else:
            self.current_date = date.replace(day=1)
        self.load_calendar()
    
    def navigate_to_event(self, event):
        """Navigate calendar to event's date"""
        event_date = event.start_date
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        self.go_to_date(event_date)
    
    def switch_events_view(self, view):
        """Switch between upcoming and recent events"""
        self.events_view = view
        
        # Update tab button styles
        if view == "upcoming":
            self.upcoming_tab.configure(
                fg_color=theme_manager.get_color("accent"),
                hover_color=theme_manager.get_color("accent_hover"),
                text_color="#ffffff"
            )
            self.recent_tab.configure(
                fg_color=theme_manager.get_color("bg_tertiary"),
                hover_color=theme_manager.get_color("border"),
                text_color=theme_manager.get_color("fg_primary")
            )
        else:
            self.recent_tab.configure(
                fg_color=theme_manager.get_color("accent"),
                hover_color=theme_manager.get_color("accent_hover"),
                text_color="#ffffff"
            )
            self.upcoming_tab.configure(
                fg_color=theme_manager.get_color("bg_tertiary"),
                hover_color=theme_manager.get_color("border"),
                text_color=theme_manager.get_color("fg_primary")
            )
        
        # Reload events list
        self.load_events_list()
    
    def show_add_event_dialog(self, event=None):
        """Show dialog to add/edit event with date and time pickers"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Event" if event else "Add Event")
        dialog.geometry("600x750")
        dialog.transient(self)
        dialog.grab_set()
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color=theme_manager.get_color("bg_primary")
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ThemedLabel(scroll_frame, text="Event Title:").pack(anchor="w", pady=(0, 5))
        title_entry = ThemedEntry(scroll_frame)
        if event:
            title_entry.insert(0, event.title)
        title_entry.pack(fill="x", pady=(0, 15))
        
        # Description
        ThemedLabel(scroll_frame, text="Description:").pack(anchor="w", pady=(0, 5))
        desc_text = ThemedTextbox(scroll_frame, height=80)
        if event and event.description:
            desc_text.insert("1.0", event.description)
        desc_text.pack(fill="x", pady=(0, 15))
        
        # Date Picker
        ThemedLabel(scroll_frame, text="Date:").pack(anchor="w", pady=(0, 5))
        date_picker = DatePicker(scroll_frame, initial_date=event.start_date if event else None)
        date_picker.pack(fill="x", pady=(0, 15))
        
        # Time Picker
        ThemedLabel(scroll_frame, text="Time:").pack(anchor="w", pady=(0, 5))
        time_picker = TimePicker(scroll_frame, initial_time=event.start_date if event else None)
        time_picker.pack(fill="x", pady=(0, 15))
        
        # Location
        ThemedLabel(scroll_frame, text="Location (optional):").pack(anchor="w", pady=(0, 5))
        location_entry = ThemedEntry(scroll_frame)
        if event and event.location:
            location_entry.insert(0, event.location)
        location_entry.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ThemedFrame(scroll_frame, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_event_data():
            try:
                title = title_entry.get().strip()
                if not title:
                    return
                
                selected_date = date_picker.get_date()
                hour, minute = time_picker.get_time()
                start_datetime = selected_date.replace(hour=hour, minute=minute)
                
                location = location_entry.get().strip()
                description = desc_text.get("1.0", "end-1c").strip()
                
                if event:
                    event.title = title
                    event.description = description if description else None
                    event.start_date = start_datetime
                    event.location = location if location else None
                    event.updated_at = datetime.now()
                    event.save()
                else:
                    Event.create(
                        title=title,
                        description=description if description else None,
                        start_date=start_datetime,
                        location=location if location else None
                    )
                
                self.load_calendar()
                dialog.destroy()
            except Exception as e:
                print(f"Error saving event: {e}")
        
        ThemedButton(btn_frame, text="Cancel", width=100, command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save Event", width=120, button_style="accent", command=save_event_data).pack(side="right")
    
    def refresh(self):
        """Refresh calendar"""
        self.load_calendar()
