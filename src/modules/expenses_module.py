"""
Lifeboat - Expenses Module
Expense and income tracking with charts
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedComboBox, SearchBar
from src.core.theme_manager import theme_manager
from src.core.database import Expense, Income, db
from datetime import datetime, timedelta
from src.core import config
from src.utils import helpers as utils
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

class ExpensesModule(ThemedFrame):
    """Expenses and income tracking module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.current_month = datetime.now()
        self.view_mode = "expenses"  # expenses or income
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup expenses UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header.grid_columnconfigure(2, weight=1)
        
        title = ThemedLabel(
            header,
            text="Financial Tracker",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # View toggle
        toggle_frame = ThemedFrame(header, color_key="bg_primary")
        toggle_frame.grid(row=0, column=1, padx=20)
        
        self.expenses_btn = ThemedButton(
            toggle_frame,
            text="Expenses",
            button_style="accent",
            width=100,
            command=lambda: self.switch_view("expenses")
        )
        self.expenses_btn.pack(side="left", padx=2)
        
        self.income_btn = ThemedButton(
            toggle_frame,
            text="Income",
            width=100,
            command=lambda: self.switch_view("income")
        )
        self.income_btn.pack(side="left", padx=2)
        
        # Month navigation
        nav_frame = ThemedFrame(header, color_key="bg_primary")
        nav_frame.grid(row=0, column=2, sticky="e")
        
        ThemedButton(
            nav_frame,
            text="◀",
            width=40,
            command=self.prev_month
        ).pack(side="left", padx=2)
        
        self.month_label = ThemedLabel(
            nav_frame,
            text="",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            width=150
        )
        self.month_label.pack(side="left", padx=10)
        
        ThemedButton(
            nav_frame,
            text="▶",
            width=40,
            command=self.next_month
        ).pack(side="left", padx=2)
        
        self.add_btn = ThemedButton(
            header,
            text="+ Add Expense",
            button_style="accent",
            command=self.show_add_dialog
        )
        self.add_btn.grid(row=0, column=3, sticky="e", padx=(20, 0))
        
        # Content area
        content = ThemedFrame(self, color_key="bg_primary")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Left side - List
        left_panel = ThemedFrame(content, color_key="bg_primary")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Summary
        self.summary_frame = ThemedFrame(left_panel, color_key="bg_secondary", corner_radius=10)
        self.summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.total_label = ThemedLabel(
            self.summary_frame,
            text="Total: $0.00",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        self.total_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.count_label = ThemedLabel(
            self.summary_frame,
            text="Transactions: 0",
            color_key="fg_secondary"
        )
        self.count_label.grid(row=0, column=1, padx=20, pady=15)
        
        self.avg_label = ThemedLabel(
            self.summary_frame,
            text="Average: $0.00",
            color_key="fg_secondary"
        )
        self.avg_label.grid(row=0, column=2, padx=20, pady=15, sticky="e")
        
        # List
        self.list_scroll = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=theme_manager.get_color("bg_primary")
        )
        self.list_scroll.grid(row=1, column=0, sticky="nsew")
        self.list_scroll.grid_columnconfigure(0, weight=1)
        
        # Right side - Charts
        right_panel = ThemedFrame(content, color_key="bg_primary")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure((0, 1), weight=1)
        
        # Category chart
        self.category_chart_frame = ThemedFrame(right_panel, color_key="bg_secondary", corner_radius=10)
        self.category_chart_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        chart_title = ThemedLabel(
            self.category_chart_frame,
            text="By Category",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        chart_title.pack(padx=15, pady=10, anchor="w")
        
        self.category_chart_container = ThemedFrame(self.category_chart_frame, color_key="bg_secondary")
        self.category_chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Trend chart
        self.trend_chart_frame = ThemedFrame(right_panel, color_key="bg_secondary", corner_radius=10)
        self.trend_chart_frame.grid(row=1, column=0, sticky="nsew")
        
        trend_title = ThemedLabel(
            self.trend_chart_frame,
            text="Daily Trend",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        trend_title.pack(padx=15, pady=10, anchor="w")
        
        self.trend_chart_container = ThemedFrame(self.trend_chart_frame, color_key="bg_secondary")
        self.trend_chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def load_data(self):
        """Load financial data"""
        # Update month label
        month_name = utils.get_month_name(self.current_month.month)
        self.month_label.configure(text=f"{month_name} {self.current_month.year}")
        
        # Get date range
        month_start = self.current_month.replace(day=1)
        if self.current_month.month == 12:
            month_end = self.current_month.replace(year=self.current_month.year + 1, month=1, day=1)
        else:
            month_end = self.current_month.replace(month=self.current_month.month + 1, day=1)
        
        # Load data based on view mode
        if self.view_mode == "expenses":
            items = list(Expense.select().where(
                (Expense.date >= month_start.date()) &
                (Expense.date < month_end.date())
            ).order_by(Expense.date.desc()))
        else:
            items = list(Income.select().where(
                (Income.date >= month_start.date()) &
                (Income.date < month_end.date())
            ).order_by(Income.date.desc()))
        
        # Update summary
        total = sum([item.amount for item in items])
        count = len(items)
        avg = total / count if count > 0 else 0
        
        self.total_label.configure(text=f"Total: {utils.format_currency(total)}")
        self.count_label.configure(text=f"Transactions: {count}")
        self.avg_label.configure(text=f"Average: {utils.format_currency(avg)}")
        
        # Load list
        self.load_list(items)
        
        # Load charts
        self.load_charts(items)
    
    def load_list(self, items):
        """Load items list"""
        # Clear existing
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        if not items:
            no_items = ThemedLabel(
                self.list_scroll,
                text=f"No {self.view_mode} this month",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE),
                color_key="fg_secondary"
            )
            no_items.pack(pady=50)
            return
        
        # Display items
        for item in items:
            self.create_item_widget(item)
    
    def create_item_widget(self, item):
        """Create item widget"""
        item_frame = ThemedFrame(self.list_scroll, color_key="bg_secondary", corner_radius=8)
        item_frame.pack(fill="x", pady=5, padx=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Amount
        amount_label = ThemedLabel(
            item_frame,
            text=utils.format_currency(item.amount),
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        amount_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Info
        info_frame = ThemedFrame(item_frame, color_key="bg_secondary")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        category_label = ThemedLabel(
            info_frame,
            text=item.category,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        )
        category_label.pack(anchor="w")
        
        if item.description:
            desc_label = ThemedLabel(
                info_frame,
                text=utils.truncate_text(item.description, 50),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
        
        # Date
        date_label = ThemedLabel(
            item_frame,
            text=utils.format_date(item.date),
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        date_label.grid(row=0, column=2, padx=15, pady=10)
        
        # Delete button
        ThemedButton(
            item_frame,
            text="×",
            width=30,
            button_style="danger",
            command=lambda: self.delete_item(item)
        ).grid(row=0, column=3, padx=10, pady=10)
    
    def load_charts(self, items):
        """Load charts"""
        # Clear existing charts
        for widget in self.category_chart_container.winfo_children():
            widget.destroy()
        for widget in self.trend_chart_container.winfo_children():
            widget.destroy()
        
        if not items:
            return
        
        # Prepare data
        df = pd.DataFrame([{
            'amount': float(item.amount),
            'category': item.category,
            'date': item.date
        } for item in items])
        
        # Category pie chart
        self.create_category_chart(df)
        
        # Trend line chart
        self.create_trend_chart(df)
    
    def create_category_chart(self, df):
        """Create category pie chart"""
        fig = Figure(figsize=(4, 3), facecolor=theme_manager.get_color("bg_secondary"))
        ax = fig.add_subplot(111)
        
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        colors = utils.generate_color_palette(theme_manager.get_color("accent"), len(category_totals))
        
        ax.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct='%1.1f%%',
            colors=colors,
            textprops={'color': theme_manager.get_color("fg_primary"), 'fontsize': 8}
        )
        
        ax.set_facecolor(theme_manager.get_color("bg_secondary"))
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.category_chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_trend_chart(self, df):
        """Create trend line chart"""
        fig = Figure(figsize=(4, 3), facecolor=theme_manager.get_color("bg_secondary"))
        ax = fig.add_subplot(111)
        
        daily_totals = df.groupby('date')['amount'].sum().sort_index()
        
        ax.plot(
            daily_totals.index,
            daily_totals.values,
            color=theme_manager.get_color("accent"),
            linewidth=2,
            marker='o',
            markersize=4
        )
        
        ax.set_facecolor(theme_manager.get_color("bg_secondary"))
        ax.tick_params(colors=theme_manager.get_color("fg_primary"), labelsize=8)
        ax.spines['bottom'].set_color(theme_manager.get_color("border"))
        ax.spines['left'].set_color(theme_manager.get_color("border"))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        fig.autofmt_xdate()
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.trend_chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def switch_view(self, mode):
        """Switch between expenses and income"""
        self.view_mode = mode
        
        if mode == "expenses":
            self.expenses_btn.configure(
                fg_color=theme_manager.get_color("accent"),
                hover_color=theme_manager.get_color("accent_hover")
            )
            self.income_btn.configure(
                fg_color=theme_manager.get_color("bg_tertiary"),
                hover_color=theme_manager.get_color("border")
            )
            self.add_btn.configure(text="+ Add Expense")
        else:
            self.expenses_btn.configure(
                fg_color=theme_manager.get_color("bg_tertiary"),
                hover_color=theme_manager.get_color("border")
            )
            self.income_btn.configure(
                fg_color=theme_manager.get_color("accent"),
                hover_color=theme_manager.get_color("accent_hover")
            )
            self.add_btn.configure(text="+ Add Income")
        
        self.load_data()
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_month.month == 1:
            self.current_month = self.current_month.replace(year=self.current_month.year - 1, month=12)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month - 1)
        self.load_data()
    
    def next_month(self):
        """Go to next month"""
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self.load_data()
    
    def show_add_dialog(self):
        """Show add expense/income dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Add {self.view_mode.capitalize()[:-1]}")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Import DatePicker
        from modules.calendar_module import DatePicker
        
        scroll_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color=theme_manager.get_color("bg_primary")
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Amount
        ThemedLabel(scroll_frame, text="Amount:").pack(anchor="w", pady=(0, 5))
        amount_entry = ThemedEntry(scroll_frame, placeholder_text="0.00")
        amount_entry.pack(fill="x", pady=(0, 15))
        
        # Category
        ThemedLabel(scroll_frame, text="Category:").pack(anchor="w", pady=(0, 5))
        categories = config.EXPENSE_CATEGORIES if self.view_mode == "expenses" else config.INCOME_CATEGORIES
        category_combo = ThemedComboBox(scroll_frame, values=categories)
        category_combo.set(categories[0])
        category_combo.pack(fill="x", pady=(0, 15))
        
        # Description
        ThemedLabel(scroll_frame, text="Description (optional):").pack(anchor="w", pady=(0, 5))
        desc_entry = ThemedEntry(scroll_frame)
        desc_entry.pack(fill="x", pady=(0, 15))
        
        # Date Picker
        ThemedLabel(scroll_frame, text="Date:").pack(anchor="w", pady=(0, 5))
        date_picker = DatePicker(scroll_frame, initial_date=datetime.now())
        date_picker.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ThemedFrame(scroll_frame, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_item():
            try:
                amount_str = amount_entry.get().strip()
                if not amount_str:
                    return
                
                # Validate amount is a number
                try:
                    amount = float(amount_str)
                except ValueError:
                    # Show error - amount must be a number
                    return
                
                date = date_picker.get_date().date()
                description = desc_entry.get().strip()
                
                if self.view_mode == "expenses":
                    Expense.create(
                        amount=amount,
                        category=category_combo.get(),
                        description=description if description else None,
                        date=date
                    )
                else:
                    Income.create(
                        amount=amount,
                        category=category_combo.get(),
                        description=description if description else None,
                        date=date
                    )
                
                self.load_data()
                dialog.destroy()
            except Exception as e:
                print(f"Error saving: {e}")
        
        ThemedButton(btn_frame, text="Cancel", width=100, command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save", width=100, button_style="accent", command=save_item).pack(side="right")
    
    def delete_item(self, item):
        """Delete an item"""
        item.delete_instance()
        self.load_data()
    
    def refresh(self):
        """Refresh data"""
        self.load_data()
