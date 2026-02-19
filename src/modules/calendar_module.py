"""
Lifeboat - Calendar Module
Calendar view with events management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, ThemedComboBox
from src.core.theme_manager import theme_manager
from src.core.database import Event, db
from datetime import datetime, timedelta
import calendar
from src.core import config
from src.utils import helpers as utils

class DatePicker(ThemedFrame):
    """Date picker widget"""
    def __init__(self, master, initial_date=None, **kwargs):
        super().__init__(master, color_key="bg_secondary", **kwargs)
        
        self.selected_date = initial_date or datetime.now()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup date picker UI"""
        # Month/Year selector
        header = ThemedFrame(self, color_key="bg_secondary")
        header.pack(fill="x", padx=5, pady=5)
        
        ThemedButton(header, text="◀", width=30, command=self.prev_month).pack(side="left")
        
        self.month_label = ThemedLabel(
            header,
            text=self.selected_date.strftime("%B %Y"),
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        self.month_label.pack(side="left", expand=True)
        
        ThemedButton(header, text="▶", width=30, command=self.next_month).pack(side="right")
        
        # Calendar grid
        self.calendar_frame = ThemedFrame(self, color_key="bg_secondary")
        self.calendar_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_calendar()
    
    def update_calendar(self):
        """Update calendar display"""
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Weekday headers
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(weekdays):
            lbl = ThemedLabel(self.calendar_frame, text=day, width=4)
            lbl.grid(row=0, column=i, padx=2, pady=2)
        
        # Calendar days
        cal = utils.get_month_calendar(self.selected_date.year, self.selected_date.month)
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                
                date = datetime(self.selected_date.year, self.selected_date.month, day)
                is_selected = date.date() == self.selected_date.date()
                
                btn = ThemedButton(
                    self.calendar_frame,
                    text=str(day),
                    width=4,
                    height=2,
                    command=lambda d=date: self.select_date(d)
                )
                
                if is_selected:
                    btn.configure(
                        fg_color=theme_manager.get_color("accent"),
                        hover_color=theme_manager.get_color("accent_hover")
                    )
                
                btn.grid(row=week_num + 1, column=day_num, padx=2, pady=2)
        
        self.month_label.configure(text=self.selected_date.strftime("%B %Y"))
    
    def select_date(self, date):
        """Select a date"""
        self.selected_date = date
        self.update_calendar()
    
    def prev_month(self):
        """Go to previous month"""
        if self.selected_date.month == 1:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year - 1, month=12)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.selected_date.month == 12:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year + 1, month=1)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month + 1)
        self.update_calendar()
    
    def get_date(self):
        """Get selected date"""
        return self.selected_date

class TimePicker(ThemedFrame):
    """Time picker widget"""
    def __init__(self, master, initial_time=None, **kwargs):
        super().__init__(master, color_key="bg_secondary", **kwargs)
        
        if initial_time:
            self.hour = initial_time.hour
            self.minute = initial_time.minute
        else:
            self.hour = 9
            self.minute = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup time picker UI"""
        # Hour selector
        hour_frame = ThemedFrame(self, color_key="bg_secondary")
        hour_frame.pack(side="left", padx=10)
        
        ThemedLabel(hour_frame, text="Hour").pack()
        
        hour_btn_frame = ThemedFrame(hour_frame, color_key="bg_secondary")
        hour_btn_frame.pack()
        
        ThemedButton(hour_btn_frame, text="▲", width=40, command=self.hour_up).pack()
        
        # Editable hour entry
        self.hour_entry = ThemedEntry(hour_btn_frame, width=60, justify="center")
        self.hour_entry.insert(0, f"{self.hour:02d}")
        self.hour_entry.bind("<FocusOut>", self.validate_hour)
        self.hour_entry.bind("<Return>", self.validate_hour)
        self.hour_entry.pack(pady=5)
        
        ThemedButton(hour_btn_frame, text="▼", width=40, command=self.hour_down).pack()
        
        # Separator
        ThemedLabel(self, text=":", font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")).pack(side="left")
        
        # Minute selector
        minute_frame = ThemedFrame(self, color_key="bg_secondary")
        minute_frame.pack(side="left", padx=10)
        
        ThemedLabel(minute_frame, text="Minute").pack()
        
        minute_btn_frame = ThemedFrame(minute_frame, color_key="bg_secondary")
        minute_btn_frame.pack()
        
        ThemedButton(minute_btn_frame, text="▲", width=40, command=self.minute_up).pack()
        
        # Editable minute entry
        self.minute_entry = ThemedEntry(minute_btn_frame, width=60, justify="center")
        self.minute_entry.insert(0, f"{self.minute:02d}")
        self.minute_entry.bind("<FocusOut>", self.validate_minute)
        self.minute_entry.bind("<Return>", self.validate_minute)
        self.minute_entry.pack(pady=5)
        
        ThemedButton(minute_btn_frame, text="▼", width=40, command=self.minute_down).pack()
    
    def validate_hour(self, event=None):
        """Validate and update hour from entry"""
        try:
            hour = int(self.hour_entry.get())
            if 0 <= hour <= 23:
                self.hour = hour
            self.hour_entry.delete(0, "end")
            self.hour_entry.insert(0, f"{self.hour:02d}")
        except:
            self.hour_entry.delete(0, "end")
            self.hour_entry.insert(0, f"{self.hour:02d}")
    
    def validate_minute(self, event=None):
        """Validate and update minute from entry"""
        try:
            minute = int(self.minute_entry.get())
            if 0 <= minute <= 59:
                self.minute = minute
            self.minute_entry.delete(0, "end")
            self.minute_entry.insert(0, f"{self.minute:02d}")
        except:
            self.minute_entry.delete(0, "end")
            self.minute_entry.insert(0, f"{self.minute:02d}")
    
    def hour_up(self):
        self.hour = (self.hour + 1) % 24
        self.hour_entry.delete(0, "end")
        self.hour_entry.insert(0, f"{self.hour:02d}")
    
    def hour_down(self):
        self.hour = (self.hour - 1) % 24
        self.hour_entry.delete(0, "end")
        self.hour_entry.insert(0, f"{self.hour:02d}")
    
    def minute_up(self):
        self.minute = (self.minute + 5) % 60
        self.minute_entry.delete(0, "end")
        self.minute_entry.insert(0, f"{self.minute:02d}")
    
    def minute_down(self):
        self.minute = (self.minute - 5) % 60
        self.minute_entry.delete(0, "end")
        self.minute_entry.insert(0, f"{self.minute:02d}")
    
    def get_time(self):
        """Get selected time as (hour, minute)"""
        self.validate_hour()
        self.validate_minute()
        return (self.hour, self.minute)

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
        
        ThemedLabel(
            events_panel,
            text="Upcoming Events",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
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
        """Load upcoming events list"""
        for widget in self.events_list.winfo_children():
            widget.destroy()
        
        # Get upcoming events
        today = datetime.now()
        events = Event.select().where(
            Event.start_date >= today
        ).order_by(Event.start_date).limit(20)
        
        if not events:
            no_events = ThemedLabel(
                self.events_list,
                text="No upcoming events",
                color_key="fg_secondary"
            )
            no_events.pack(pady=20)
            return
        
        for event in events:
            event_frame = ThemedFrame(self.events_list, color_key="bg_tertiary", corner_radius=8)
            event_frame.pack(fill="x", pady=5, padx=5)
            event_frame.grid_columnconfigure(0, weight=1)
            
            # Title
            title_label = ThemedLabel(
                event_frame,
                text=event.title,
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
            )
            title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
            
            # Date/Time
            date_label = ThemedLabel(
                event_frame,
                text=utils.format_datetime(event.start_date),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary"
            )
            date_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
            
            # Location
            if event.location:
                loc_label = ThemedLabel(
                    event_frame,
                    text=f"📍 {event.location}",
                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                    color_key="fg_secondary"
                )
                loc_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
            
            # Actions
            actions_frame = ThemedFrame(event_frame, color_key="bg_tertiary")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
            
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
