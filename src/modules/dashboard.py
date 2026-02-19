"""
Lifeboat - Dashboard Module
Main dashboard with overview of all features
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, StatCard, ThemedButton
from src.core.theme_manager import theme_manager
from src.core.database import Task, Event, Expense, Income, Goal
from datetime import datetime, timedelta
from src.core import config
from src.utils import helpers as utils

class DashboardModule(ThemedFrame):
    """Dashboard module showing overview"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title = ThemedLabel(
            header,
            text="Dashboard",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.pack(side="left")
        
        date_label = ThemedLabel(
            header,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            color_key="fg_secondary"
        )
        date_label.pack(side="right")
        
        # Content area
        content = ThemedFrame(self, color_key="bg_primary")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Stats cards
        self.tasks_card = StatCard(content, "Tasks Today", "0")
        self.tasks_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.events_card = StatCard(content, "Upcoming Events", "0")
        self.events_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.goals_card = StatCard(content, "Active Goals", "0")
        self.goals_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Financial overview
        finance_frame = ThemedFrame(content, color_key="bg_secondary", corner_radius=10)
        finance_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        finance_frame.grid_columnconfigure(0, weight=1)
        
        finance_title = ThemedLabel(
            finance_frame,
            text="This Month's Finances",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        finance_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.income_label = ThemedLabel(
            finance_frame,
            text="Income: $0.00",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        )
        self.income_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.expense_label = ThemedLabel(
            finance_frame,
            text="Expenses: $0.00",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        )
        self.expense_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.balance_label = ThemedLabel(
            finance_frame,
            text="Balance: $0.00",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        self.balance_label.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="w")
        
        # Recent tasks
        tasks_frame = ThemedFrame(content, color_key="bg_secondary", corner_radius=10)
        tasks_frame.grid(row=1, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")
        tasks_frame.grid_columnconfigure(0, weight=1)
        tasks_frame.grid_rowconfigure(1, weight=1)
        
        tasks_title = ThemedLabel(
            tasks_frame,
            text="Upcoming Tasks",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        tasks_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.tasks_list = ThemedFrame(tasks_frame, color_key="bg_secondary")
        self.tasks_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Quick actions
        actions_frame = ThemedFrame(content, color_key="bg_secondary", corner_radius=10)
        actions_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        actions_title = ThemedLabel(
            actions_frame,
            text="Quick Actions",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        actions_title.pack(padx=20, pady=15, anchor="w")
        
        buttons_frame = ThemedFrame(actions_frame, color_key="bg_secondary")
        buttons_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        ThemedButton(buttons_frame, text="Add Task", button_style="accent", width=120).pack(side="left", padx=5)
        ThemedButton(buttons_frame, text="Add Event", button_style="accent", width=120).pack(side="left", padx=5)
        ThemedButton(buttons_frame, text="Add Expense", button_style="accent", width=120).pack(side="left", padx=5)
    
    def load_data(self):
        """Load dashboard data"""
        today = datetime.now().date()
        
        # Tasks today
        tasks_today = Task.select().where(
            (Task.due_date >= datetime.combine(today, datetime.min.time())) &
            (Task.due_date < datetime.combine(today + timedelta(days=1), datetime.min.time())) &
            (Task.completed == False)
        ).count()
        self.tasks_card.update_value(tasks_today)
        
        # Upcoming events (next 7 days)
        week_later = today + timedelta(days=7)
        events_count = Event.select().where(
            (Event.start_date >= datetime.combine(today, datetime.min.time())) &
            (Event.start_date < datetime.combine(week_later, datetime.min.time()))
        ).count()
        self.events_card.update_value(events_count)
        
        # Active goals
        active_goals = Goal.select().where(Goal.completed == False).count()
        self.goals_card.update_value(active_goals)
        
        # Financial data
        month_start = today.replace(day=1)
        total_income = sum([i.amount for i in Income.select().where(
            Income.date >= month_start
        )])
        total_expenses = sum([e.amount for e in Expense.select().where(
            Expense.date >= month_start
        )])
        balance = total_income - total_expenses
        
        self.income_label.configure(text=f"Income: {utils.format_currency(total_income)}")
        self.expense_label.configure(text=f"Expenses: {utils.format_currency(total_expenses)}")
        self.balance_label.configure(text=f"Balance: {utils.format_currency(balance)}")
        
        # Load upcoming tasks
        self.load_upcoming_tasks()
    
    def load_upcoming_tasks(self):
        """Load upcoming tasks list"""
        # Clear existing
        for widget in self.tasks_list.winfo_children():
            widget.destroy()
        
        # Get upcoming tasks
        tasks = Task.select().where(
            Task.completed == False
        ).order_by(Task.due_date).limit(5)
        
        if not tasks:
            no_tasks = ThemedLabel(
                self.tasks_list,
                text="No upcoming tasks",
                color_key="fg_secondary"
            )
            no_tasks.pack(pady=20)
        else:
            for task in tasks:
                task_item = ThemedFrame(self.tasks_list, color_key="bg_tertiary", corner_radius=5)
                task_item.pack(fill="x", padx=10, pady=5)
                
                task_label = ThemedLabel(
                    task_item,
                    text=task.title,
                    font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
                )
                task_label.pack(side="left", padx=10, pady=8)
                
                if task.due_date:
                    due_label = ThemedLabel(
                        task_item,
                        text=utils.format_date(task.due_date),
                        font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                        color_key="fg_secondary"
                    )
                    due_label.pack(side="right", padx=10, pady=8)
    
    def refresh(self):
        """Refresh dashboard data"""
        self.load_data()
