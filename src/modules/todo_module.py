"""
Lifeboat - Todo Module
Minimal, modern todo list with daily/weekly/monthly views
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry
from src.core.theme_manager import theme_manager
from src.core.database import Task, db
from datetime import datetime, timedelta
from src.core import config

class TodoModule(ThemedFrame):
    """Minimal todo list module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.filter_period = "Daily"  # Daily, Weekly, Monthly
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_todos()
    
    def setup_ui(self):
        """Setup minimal todo UI"""
        # Header with period filters
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=30)
        header.grid_columnconfigure(1, weight=1)
        
        # Period filter buttons
        filter_frame = ThemedFrame(header, color_key="bg_primary")
        filter_frame.grid(row=0, column=0, sticky="w")
        
        self.period_buttons = {}
        for period in ["Daily", "Weekly", "Monthly"]:
            btn = ThemedButton(
                filter_frame,
                text=period,
                width=100,
                height=35,
                command=lambda p=period: self.set_period(p)
            )
            btn.pack(side="left", padx=5)
            self.period_buttons[period] = btn
        
        # Update button styles
        self.update_period_buttons()
        
        # Date display
        self.date_label = ThemedLabel(
            header,
            text=self.get_period_text(),
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        self.date_label.grid(row=0, column=1, sticky="")
        
        # Quick add input
        add_frame = ThemedFrame(self, color_key="bg_primary")
        add_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        add_frame.grid_columnconfigure(0, weight=1)
        
        self.quick_add_entry = ThemedEntry(
            add_frame,
            placeholder_text="Add a new todo...",
            height=45,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        )
        self.quick_add_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.quick_add_entry.bind("<Return>", lambda e: self.quick_add_todo())
        
        ThemedButton(
            add_frame,
            text="Add",
            button_style="accent",
            width=80,
            height=45,
            command=self.quick_add_todo
        ).grid(row=0, column=1)
        
        # Todo list
        self.todos_container = ThemedFrame(self, color_key="bg_primary")
        self.todos_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.todos_container.grid_columnconfigure(0, weight=1)
        self.todos_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame
        self.todos_scroll = ctk.CTkScrollableFrame(
            self.todos_container,
            fg_color=theme_manager.get_color("bg_primary")
        )
        self.todos_scroll.grid(row=0, column=0, sticky="nsew")
        self.todos_scroll.grid_columnconfigure(0, weight=1)
    
    def get_period_text(self):
        """Get text for current period"""
        today = datetime.now()
        if self.filter_period == "Daily":
            return today.strftime("%A, %B %d, %Y")
        elif self.filter_period == "Weekly":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return f"Week of {start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
        else:  # Monthly
            return today.strftime("%B %Y")
    
    def set_period(self, period):
        """Set filter period"""
        self.filter_period = period
        self.update_period_buttons()
        self.date_label.configure(text=self.get_period_text())
        self.load_todos()
    
    def update_period_buttons(self):
        """Update period button styles"""
        for period, btn in self.period_buttons.items():
            if period == self.filter_period:
                btn.configure(
                    fg_color=theme_manager.get_color("accent"),
                    hover_color=theme_manager.get_color("accent_hover")
                )
            else:
                btn.configure(
                    fg_color=theme_manager.get_color("bg_tertiary"),
                    hover_color=theme_manager.get_color("border")
                )
    
    def load_todos(self):
        """Load and display todos for current period"""
        # Clear existing
        for widget in self.todos_scroll.winfo_children():
            widget.destroy()
        
        # Get date range
        today = datetime.now()
        if self.filter_period == "Daily":
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif self.filter_period == "Weekly":
            start_date = today - timedelta(days=today.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        else:  # Monthly
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if today.month == 12:
                end_date = start_date.replace(year=today.year + 1, month=1)
            else:
                end_date = start_date.replace(month=today.month + 1)
        
        # Query todos
        query = Task.select().where(
            (Task.due_date >= start_date) & (Task.due_date < end_date)
        ).order_by(Task.completed, Task.due_date)
        
        todos = list(query)
        
        if not todos:
            no_todos = ThemedLabel(
                self.todos_scroll,
                text=f"No todos for this {self.filter_period.lower()} period",
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
                color_key="fg_secondary"
            )
            no_todos.pack(pady=50)
            return
        
        # Display todos
        for todo in todos:
            self.create_todo_item(todo)
    
    def create_todo_item(self, todo):
        """Create a minimal todo item"""
        item = ThemedFrame(self.todos_scroll, color_key="bg_secondary", corner_radius=8)
        item.pack(fill="x", pady=3, padx=2)
        item.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            item,
            text="",
            width=24,
            command=lambda: self.toggle_todo(todo),
            fg_color=theme_manager.get_color("accent"),
            hover_color=theme_manager.get_color("accent_hover")
        )
        if todo.completed:
            checkbox.select()
        checkbox.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        # Title
        title_text = todo.title
        if todo.completed:
            title_text = f"✓ {title_text}"
        
        title = ThemedLabel(
            item,
            text=title_text,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            anchor="w"
        )
        if todo.completed:
            title.configure(text_color=theme_manager.get_color("fg_secondary"))
        title.grid(row=0, column=1, sticky="ew", padx=10, pady=12)
        
        # Delete button (appears on hover)
        delete_btn = ThemedButton(
            item,
            text="×",
            width=30,
            height=30,
            button_style="danger",
            command=lambda: self.delete_todo(todo)
        )
        delete_btn.grid(row=0, column=2, padx=10, pady=12)
    
    def quick_add_todo(self):
        """Quickly add a new todo"""
        title = self.quick_add_entry.get().strip()
        if not title:
            return
        
        # Set due date based on current period
        today = datetime.now()
        if self.filter_period == "Daily":
            due_date = today.replace(hour=23, minute=59, second=59)
        elif self.filter_period == "Weekly":
            # End of week
            days_until_sunday = 6 - today.weekday()
            due_date = today + timedelta(days=days_until_sunday)
            due_date = due_date.replace(hour=23, minute=59, second=59)
        else:  # Monthly
            # End of month
            if today.month == 12:
                due_date = today.replace(year=today.year + 1, month=1, day=1)
            else:
                due_date = today.replace(month=today.month + 1, day=1)
            due_date = due_date - timedelta(days=1)
            due_date = due_date.replace(hour=23, minute=59, second=59)
        
        Task.create(
            title=title,
            priority="Medium",
            status="Not Started",
            due_date=due_date
        )
        
        self.quick_add_entry.delete(0, "end")
        self.load_todos()
    
    def toggle_todo(self, todo):
        """Toggle todo completion"""
        todo.completed = not todo.completed
        if todo.completed:
            todo.completed_at = datetime.now()
            todo.status = "Completed"
        else:
            todo.completed_at = None
            todo.status = "Not Started"
        todo.save()
        self.load_todos()
    
    def delete_todo(self, todo):
        """Delete a todo"""
        todo.delete_instance()
        self.load_todos()
    
    def refresh(self):
        """Refresh todos"""
        self.date_label.configure(text=self.get_period_text())
        self.load_todos()
