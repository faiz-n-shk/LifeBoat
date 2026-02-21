"""
Lifeboat - Date and Time Picker Components
Reusable date and time picker widgets for use across modules
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry
from src.core.theme_manager import theme_manager
from datetime import datetime
from src.core import config
from src.utils import helpers as utils


class DatePicker(ThemedFrame):
    """
    Date picker widget with calendar view
    
    Usage:
        picker = DatePicker(parent, initial_date=datetime.now())
        selected_date = picker.get_date()
    """
    
    def __init__(self, master, initial_date=None, **kwargs):
        """
        Initialize date picker
        
        Args:
            master: Parent widget
            initial_date: Initial date to display (default: today)
            **kwargs: Additional arguments for ThemedFrame
        """
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
        """
        Select a date
        
        Args:
            date: datetime object to select
        """
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
        """
        Get selected date
        
        Returns:
            datetime: Selected date
        """
        return self.selected_date


class TimePicker(ThemedFrame):
    """
    Time picker widget with hour and minute selectors
    
    Usage:
        picker = TimePicker(parent, initial_time=datetime.now())
        hour, minute = picker.get_time()
    """
    
    def __init__(self, master, initial_time=None, **kwargs):
        """
        Initialize time picker
        
        Args:
            master: Parent widget
            initial_time: Initial time to display (default: 09:00)
            **kwargs: Additional arguments for ThemedFrame
        """
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
        """
        Validate and update hour from entry
        
        Args:
            event: Event object (optional)
        """
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
        """
        Validate and update minute from entry
        
        Args:
            event: Event object (optional)
        """
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
        """Increment hour by 1"""
        self.hour = (self.hour + 1) % 24
        self.hour_entry.delete(0, "end")
        self.hour_entry.insert(0, f"{self.hour:02d}")
    
    def hour_down(self):
        """Decrement hour by 1"""
        self.hour = (self.hour - 1) % 24
        self.hour_entry.delete(0, "end")
        self.hour_entry.insert(0, f"{self.hour:02d}")
    
    def minute_up(self):
        """Increment minute by 5"""
        self.minute = (self.minute + 5) % 60
        self.minute_entry.delete(0, "end")
        self.minute_entry.insert(0, f"{self.minute:02d}")
    
    def minute_down(self):
        """Decrement minute by 5"""
        self.minute = (self.minute - 5) % 60
        self.minute_entry.delete(0, "end")
        self.minute_entry.insert(0, f"{self.minute:02d}")
    
    def get_time(self):
        """
        Get selected time
        
        Returns:
            tuple: (hour, minute) as integers
        """
        self.validate_hour()
        self.validate_minute()
        return (self.hour, self.minute)
