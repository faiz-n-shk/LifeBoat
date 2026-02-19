"""
Lifeboat - Habits Module
Habit tracking and management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, ThemedComboBox, ColorPickerButton
from src.core.theme_manager import theme_manager
from src.core.database import Habit, HabitLog, db
from datetime import datetime, timedelta
from src.core import config
from src.utils import helpers as utils
import calendar

class HabitsModule(ThemedFrame):
    """Habits tracking module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.current_date = datetime.now()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_habits()
    
    def setup_ui(self):
        """Setup habits UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header.grid_columnconfigure(1, weight=1)
        
        title = ThemedLabel(
            header,
            text="Habit Tracker",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # Date navigation
        nav_frame = ThemedFrame(header, color_key="bg_primary")
        nav_frame.grid(row=0, column=1, sticky="e")
        
        ThemedButton(
            nav_frame,
            text="◀",
            width=40,
            command=self.prev_week
        ).pack(side="left", padx=2)
        
        self.week_label = ThemedLabel(
            nav_frame,
            text="",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            width=200
        )
        self.week_label.pack(side="left", padx=10)
        
        ThemedButton(
            nav_frame,
            text="▶",
            width=40,
            command=self.next_week
        ).pack(side="left", padx=2)
        
        ThemedButton(
            nav_frame,
            text="Today",
            width=80,
            command=self.go_to_today
        ).pack(side="left", padx=10)
        
        ThemedButton(
            header,
            text="+ Add Habit",
            button_style="accent",
            command=self.show_add_habit_dialog
        ).grid(row=0, column=2, sticky="e")
        
        # Habits list
        self.habits_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=theme_manager.get_color("bg_primary")
        )
        self.habits_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.habits_scroll.grid_columnconfigure(0, weight=1)
    
    def load_habits(self):
        """Load and display habits"""
        # Update week label
        week_dates = utils.get_week_dates(self.current_date)
        start_date = week_dates[0]
        end_date = week_dates[-1]
        self.week_label.configure(
            text=f"{utils.format_date(start_date, '%b %d')} - {utils.format_date(end_date, '%b %d, %Y')}"
        )
        
        # Clear existing
        for widget in self.habits_scroll.winfo_children():
            widget.destroy()
        
        habits = list(Habit.select().order_by(Habit.created_at))
        
        if not habits:
            no_habits = ThemedLabel(
                self.habits_scroll,
                text="No habits yet. Create one to start tracking!",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE),
                color_key="fg_secondary"
            )
            no_habits.pack(pady=50)
            return
        
        # Week header
        header_frame = ThemedFrame(self.habits_scroll, color_key="bg_primary")
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ThemedLabel(
            header_frame,
            text="Habit",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"),
            width=200
        ).grid(row=0, column=0, sticky="w", padx=10)
        
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            ThemedLabel(
                header_frame,
                text=day,
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"),
                width=50
            ).grid(row=0, column=i+1, padx=5)
        
        # Display habits
        for habit in habits:
            self.create_habit_widget(habit, week_dates)
    
    def create_habit_widget(self, habit, week_dates):
        """Create habit tracking widget"""
        habit_frame = ThemedFrame(self.habits_scroll, color_key="bg_secondary", corner_radius=10)
        habit_frame.pack(fill="x", pady=5)
        habit_frame.grid_columnconfigure(0, weight=1)
        
        # Habit info
        info_frame = ThemedFrame(habit_frame, color_key="bg_secondary")
        info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Color indicator
        color_box = ThemedFrame(info_frame, corner_radius=5)
        color_box.configure(fg_color=habit.color, width=5, height=30)
        color_box.pack(side="left", padx=(0, 10))
        
        name_frame = ThemedFrame(info_frame, color_key="bg_secondary")
        name_frame.pack(side="left")
        
        name_label = ThemedLabel(
            name_frame,
            text=habit.name,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        name_label.pack(anchor="w")
        
        freq_label = ThemedLabel(
            name_frame,
            text=f"{habit.frequency} • Target: {habit.target_count}x",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        freq_label.pack(anchor="w")
        
        # Week checkboxes
        for i, date in enumerate(week_dates):
            # Check if logged for this date
            log = HabitLog.get_or_none(
                (HabitLog.habit == habit) &
                (HabitLog.date == date.date())
            )
            
            is_today = date.date() == datetime.now().date()
            
            checkbox_frame = ThemedFrame(
                habit_frame,
                color_key="bg_tertiary" if is_today else "bg_secondary"
            )
            checkbox_frame.grid(row=0, column=i+1, padx=5, pady=10)
            
            checkbox = ctk.CTkCheckBox(
                checkbox_frame,
                text="",
                width=30,
                command=lambda h=habit, d=date: self.toggle_habit_log(h, d),
                fg_color=habit.color,
                hover_color=habit.color
            )
            if log and log.completed:
                checkbox.select()
            checkbox.pack()
        
        # Actions
        actions_frame = ThemedFrame(habit_frame, color_key="bg_secondary")
        actions_frame.grid(row=0, column=8, padx=15, pady=15)
        
        ThemedButton(
            actions_frame,
            text="Edit",
            width=60,
            command=lambda: self.edit_habit(habit)
        ).pack(side="left", padx=2)
        
        ThemedButton(
            actions_frame,
            text="Delete",
            button_style="danger",
            width=60,
            command=lambda: self.delete_habit(habit)
        ).pack(side="left", padx=2)
    
    def toggle_habit_log(self, habit, date):
        """Toggle habit completion for a date"""
        log = HabitLog.get_or_none(
            (HabitLog.habit == habit) &
            (HabitLog.date == date.date())
        )
        
        if log:
            log.delete_instance()
        else:
            HabitLog.create(
                habit=habit,
                date=date.date(),
                completed=True
            )
        
        self.load_habits()
    
    def prev_week(self):
        """Go to previous week"""
        self.current_date -= timedelta(days=7)
        self.load_habits()
    
    def next_week(self):
        """Go to next week"""
        self.current_date += timedelta(days=7)
        self.load_habits()
    
    def go_to_today(self):
        """Go to current week"""
        self.current_date = datetime.now()
        self.load_habits()
    
    def show_add_habit_dialog(self):
        """Show add habit dialog"""
        self.show_habit_dialog()
    
    def edit_habit(self, habit):
        """Edit habit"""
        self.show_habit_dialog(habit)
    
    def show_habit_dialog(self, habit=None):
        """Show habit dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Habit" if habit else "Add Habit")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        content = ThemedFrame(dialog, color_key="bg_primary")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ThemedLabel(content, text="Habit Name:").pack(anchor="w", pady=(0, 5))
        name_entry = ThemedEntry(content)
        if habit:
            name_entry.insert(0, habit.name)
        name_entry.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Description:").pack(anchor="w", pady=(0, 5))
        desc_text = ThemedTextbox(content, height=80)
        if habit and habit.description:
            desc_text.insert("1.0", habit.description)
        desc_text.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Frequency:").pack(anchor="w", pady=(0, 5))
        freq_combo = ThemedComboBox(content, values=["Daily", "Weekly", "Monthly"])
        freq_combo.set(habit.frequency if habit else "Daily")
        freq_combo.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Target Count:").pack(anchor="w", pady=(0, 5))
        target_entry = ThemedEntry(content)
        target_entry.insert(0, str(habit.target_count) if habit else "1")
        target_entry.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Color:").pack(anchor="w", pady=(0, 5))
        color_picker = ColorPickerButton(
            content,
            initial_color=habit.color if habit else theme_manager.get_color("accent")
        )
        color_picker.pack(anchor="w", pady=(0, 15))
        
        btn_frame = ThemedFrame(content, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_habit():
            try:
                if habit:
                    habit.name = name_entry.get()
                    habit.description = desc_text.get("1.0", "end-1c")
                    habit.frequency = freq_combo.get()
                    habit.target_count = int(target_entry.get())
                    habit.color = color_picker.get_color()
                    habit.save()
                else:
                    Habit.create(
                        name=name_entry.get(),
                        description=desc_text.get("1.0", "end-1c"),
                        frequency=freq_combo.get(),
                        target_count=int(target_entry.get()),
                        color=color_picker.get_color()
                    )
                
                self.load_habits()
                dialog.destroy()
            except Exception as e:
                print(f"Error saving habit: {e}")
        
        ThemedButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save", button_style="accent", command=save_habit).pack(side="right")
    
    def delete_habit(self, habit):
        """Delete habit"""
        # Delete all logs
        HabitLog.delete().where(HabitLog.habit == habit).execute()
        # Delete habit
        habit.delete_instance()
        self.load_habits()
    
    def refresh(self):
        """Refresh habits"""
        self.load_habits()
