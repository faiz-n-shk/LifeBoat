"""
Lifeboat - Tasks Module
task management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, ThemedComboBox
from src.core.theme_manager import theme_manager
from src.core.database import Task, db
from datetime import datetime, timedelta
from src.core import config
from src.utils import helpers as utils

class TasksModule(ThemedFrame):
    """tasks management module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.view_mode = "Table"  # Table, Board, List
        self.filter_status = "All"
        self.sort_by = "Due Date"
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """setup tasks UI"""
        # Header with title and actions
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        header.grid_columnconfigure(0, weight=1)
        
        # Title and view controls
        title_row = ThemedFrame(header, color_key="bg_primary")
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        title_row.grid_columnconfigure(0, weight=1)
        
        title = ThemedLabel(
            title_row,
            text="📋 Tasks",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # View mode buttons
        view_frame = ThemedFrame(title_row, color_key="bg_primary")
        view_frame.grid(row=0, column=1, sticky="e", padx=(0, 15))
        
        self.view_buttons = {}
        for view in ["Table", "Board", "List"]:
            btn = ThemedButton(
                view_frame,
                text=view,
                width=80,
                height=32,
                command=lambda v=view: self.set_view(v)
            )
            btn.pack(side="left", padx=2)
            self.view_buttons[view] = btn
        
        self.update_view_buttons()
        
        # New task button
        ThemedButton(
            title_row,
            text="+ New Task",
            button_style="accent",
            height=32,
            command=self.show_add_task_dialog
        ).grid(row=0, column=2, sticky="e")
        
        # Filters and sorting
        controls_row = ThemedFrame(header, color_key="bg_primary")
        controls_row.grid(row=1, column=0, sticky="ew")
        
        ThemedLabel(controls_row, text="Filter:").pack(side="left", padx=(0, 5))
        
        self.status_filter = ThemedComboBox(
            controls_row,
            values=["All", "Active", "Completed"] + config.TASK_STATUSES,
            command=self.on_filter_change,
            width=150
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=5)
        
        ThemedLabel(controls_row, text="Sort by:").pack(side="left", padx=(15, 5))
        
        self.sort_combo = ThemedComboBox(
            controls_row,
            values=["Due Date", "Priority", "Status", "Created Date", "Title"],
            command=self.on_sort_change,
            width=150
        )
        self.sort_combo.set("Due Date")
        self.sort_combo.pack(side="left", padx=5)
        
        # Tasks container
        self.tasks_container = ThemedFrame(self, color_key="bg_primary")
        self.tasks_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.tasks_container.grid_columnconfigure(0, weight=1)
        self.tasks_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame
        self.tasks_scroll = ctk.CTkScrollableFrame(
            self.tasks_container,
            fg_color=theme_manager.get_color("bg_primary")
        )
        self.tasks_scroll.grid(row=0, column=0, sticky="nsew")
        self.tasks_scroll.grid_columnconfigure(0, weight=1)
    
    def set_view(self, view):
        """Set view mode"""
        self.view_mode = view
        self.update_view_buttons()
        self.load_tasks()
    
    def update_view_buttons(self):
        """Update view button styles"""
        for view, btn in self.view_buttons.items():
            if view == self.view_mode:
                btn.configure(
                    fg_color=theme_manager.get_color("accent"),
                    hover_color=theme_manager.get_color("accent_hover")
                )
            else:
                btn.configure(
                    fg_color=theme_manager.get_color("bg_tertiary"),
                    hover_color=theme_manager.get_color("border")
                )
    
    def load_tasks(self):
        """Load and display tasks"""
        # Clear existing
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()
        
        # Build query
        query = Task.select()
        
        # Apply filters
        if self.filter_status == "Active":
            query = query.where(Task.completed == False)
        elif self.filter_status == "Completed":
            query = query.where(Task.completed == True)
        elif self.filter_status != "All":
            query = query.where(Task.status == self.filter_status)
        
        # Apply sorting
        if self.sort_by == "Due Date":
            query = query.order_by(Task.due_date.desc(nulls='LAST'))
        elif self.sort_by == "Priority":
            priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
            tasks = sorted(list(query), key=lambda t: priority_order.get(t.priority, 4))
        elif self.sort_by == "Status":
            query = query.order_by(Task.status)
            tasks = list(query)
        elif self.sort_by == "Created Date":
            query = query.order_by(Task.created_at.desc())
            tasks = list(query)
        elif self.sort_by == "Title":
            query = query.order_by(Task.title)
            tasks = list(query)
        
        if self.sort_by != "Priority":
            tasks = list(query)
        
        if not tasks:
            no_tasks = ThemedLabel(
                self.tasks_scroll,
                text="No tasks yet. Create your first task!",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE),
                color_key="fg_secondary"
            )
            no_tasks.pack(pady=50)
            return
        
        # Display based on view mode
        if self.view_mode == "Table":
            self.display_table_view(tasks)
        elif self.view_mode == "Board":
            self.display_board_view(tasks)
        else:  # List
            self.display_list_view(tasks)
    
    def display_table_view(self, tasks):
        """Display tasks in table view"""
        # Table header
        header = ThemedFrame(self.tasks_scroll, color_key="bg_secondary", corner_radius=8)
        header.pack(fill="x", pady=(0, 10), padx=2)
        header.grid_columnconfigure(1, weight=1)
        
        ThemedLabel(header, text="", width=40).grid(row=0, column=0, padx=15, pady=10)
        ThemedLabel(header, text="Task", font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=10)
        ThemedLabel(header, text="Status", font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"), width=120).grid(row=0, column=2, padx=10, pady=10)
        ThemedLabel(header, text="Priority", font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"), width=100).grid(row=0, column=3, padx=10, pady=10)
        ThemedLabel(header, text="Due Date", font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"), width=120).grid(row=0, column=4, padx=10, pady=10)
        ThemedLabel(header, text="Actions", font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"), width=120).grid(row=0, column=5, padx=10, pady=10)
        
        # Table rows
        for task in tasks:
            self.create_table_row(task)
    
    def create_table_row(self, task):
        """Create a table row for a task"""
        row = ThemedFrame(self.tasks_scroll, color_key="bg_secondary", corner_radius=6)
        row.pack(fill="x", pady=2, padx=2)
        row.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            row,
            text="",
            width=24,
            command=lambda: self.toggle_task(task),
            fg_color=theme_manager.get_color("accent"),
            hover_color=theme_manager.get_color("accent_hover")
        )
        if task.completed:
            checkbox.select()
        checkbox.grid(row=0, column=0, padx=15, pady=12)
        
        # Task title
        title_frame = ThemedFrame(row, color_key="bg_secondary")
        title_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=12)
        
        title = ThemedLabel(
            title_frame,
            text=task.title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"),
            anchor="w"
        )
        if task.completed:
            title.configure(text_color=theme_manager.get_color("fg_secondary"))
        title.pack(anchor="w")
        
        if task.description:
            desc = ThemedLabel(
                title_frame,
                text=utils.truncate_text(task.description, 60),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary",
                anchor="w"
            )
            desc.pack(anchor="w", pady=(2, 0))
        
        # Status badge
        status_label = ThemedLabel(
            row,
            text=task.status,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            width=120
        )
        status_label.grid(row=0, column=2, padx=10, pady=12)
        
        # Priority badge
        priority_colors = {
            "Low": theme_manager.get_color("fg_secondary"),
            "Medium": theme_manager.get_color("warning"),
            "High": theme_manager.get_color("danger"),
            "Urgent": theme_manager.get_color("danger")
        }
        
        priority_label = ThemedLabel(
            row,
            text=f"⬤ {task.priority}",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            width=100
        )
        priority_label.configure(text_color=priority_colors.get(task.priority, "#ffffff"))
        priority_label.grid(row=0, column=3, padx=10, pady=12)
        
        # Due date
        due_text = "No date"
        if task.due_date:
            due_text = utils.format_date(task.due_date)
            days_until = utils.get_days_until(task.due_date)
            if days_until < 0:
                due_text += " ⚠"
        
        due_label = ThemedLabel(
            row,
            text=due_text,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary",
            width=120
        )
        due_label.grid(row=0, column=4, padx=10, pady=12)
        
        # Actions
        actions_frame = ThemedFrame(row, color_key="bg_secondary")
        actions_frame.grid(row=0, column=5, padx=10, pady=12)
        
        ThemedButton(
            actions_frame,
            text="Edit",
            width=50,
            height=28,
            command=lambda: self.edit_task(task)
        ).pack(side="left", padx=2)
        
        ThemedButton(
            actions_frame,
            text="×",
            button_style="danger",
            width=28,
            height=28,
            command=lambda: self.delete_task(task)
        ).pack(side="left", padx=2)
    
    def display_board_view(self, tasks):
        """Display tasks in Kanban board view"""
        board = ThemedFrame(self.tasks_scroll, color_key="bg_primary")
        board.pack(fill="both", expand=True)
        
        # Create columns for each status
        statuses = ["Not Started", "In Progress", "Completed"]
        for i, status in enumerate(statuses):
            board.grid_columnconfigure(i, weight=1, uniform="column")
            
            column = ThemedFrame(board, color_key="bg_secondary", corner_radius=10)
            column.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            
            # Column header
            header = ThemedLabel(
                column,
                text=f"{status} ({len([t for t in tasks if t.status == status])})",
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
            )
            header.pack(padx=15, pady=15)
            
            # Tasks in this column
            for task in tasks:
                if task.status == status or (status == "Completed" and task.completed):
                    self.create_board_card(column, task)
    
    def create_board_card(self, parent, task):
        """Create a card for board view"""
        card = ThemedFrame(parent, color_key="bg_tertiary", corner_radius=8)
        card.pack(fill="x", padx=10, pady=5)
        
        # Title
        title = ThemedLabel(
            card,
            text=task.title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"),
            anchor="w",
            wraplength=200
        )
        title.pack(anchor="w", padx=12, pady=(12, 5))
        
        # Description
        if task.description:
            desc = ThemedLabel(
                card,
                text=utils.truncate_text(task.description, 80),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary",
                anchor="w",
                wraplength=200
            )
            desc.pack(anchor="w", padx=12, pady=(0, 8))
        
        # Metadata
        meta_frame = ThemedFrame(card, color_key="bg_tertiary")
        meta_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        # Priority
        priority_colors = {
            "Low": theme_manager.get_color("fg_secondary"),
            "Medium": theme_manager.get_color("warning"),
            "High": theme_manager.get_color("danger"),
            "Urgent": theme_manager.get_color("danger")
        }
        
        priority_label = ThemedLabel(
            meta_frame,
            text=f"⬤ {task.priority}",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL)
        )
        priority_label.configure(text_color=priority_colors.get(task.priority, "#ffffff"))
        priority_label.pack(side="left")
        
        # Due date
        if task.due_date:
            due_label = ThemedLabel(
                meta_frame,
                text=f"📅 {utils.format_date(task.due_date)}",
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary"
            )
            due_label.pack(side="right")
        
        # Actions on click
        card.bind("<Button-1>", lambda e: self.edit_task(task))
    
    def display_list_view(self, tasks):
        """Display tasks in simple list view"""
        for task in tasks:
            self.create_list_item(task)
    
    def create_list_item(self, task):
        """Create a list item for a task"""
        item = ThemedFrame(self.tasks_scroll, color_key="bg_secondary", corner_radius=8)
        item.pack(fill="x", pady=3, padx=2)
        item.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            item,
            text="",
            width=24,
            command=lambda: self.toggle_task(task),
            fg_color=theme_manager.get_color("accent"),
            hover_color=theme_manager.get_color("accent_hover")
        )
        if task.completed:
            checkbox.select()
        checkbox.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Task info
        info_frame = ThemedFrame(item, color_key="bg_secondary")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=15)
        
        title = ThemedLabel(
            info_frame,
            text=task.title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"),
            anchor="w"
        )
        if task.completed:
            title.configure(text_color=theme_manager.get_color("fg_secondary"))
        title.pack(anchor="w")
        
        if task.description:
            desc = ThemedLabel(
                info_frame,
                text=utils.truncate_text(task.description, 100),
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary",
                anchor="w"
            )
            desc.pack(anchor="w", pady=(3, 0))
        
        # Metadata
        meta_frame = ThemedFrame(info_frame, color_key="bg_secondary")
        meta_frame.pack(anchor="w", pady=(5, 0))
        
        # Priority
        priority_colors = {
            "Low": theme_manager.get_color("fg_secondary"),
            "Medium": theme_manager.get_color("warning"),
            "High": theme_manager.get_color("danger"),
            "Urgent": theme_manager.get_color("danger")
        }
        
        priority_label = ThemedLabel(
            meta_frame,
            text=f"⬤ {task.priority}",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL)
        )
        priority_label.configure(text_color=priority_colors.get(task.priority, "#ffffff"))
        priority_label.pack(side="left", padx=(0, 15))
        
        # Status
        status_label = ThemedLabel(
            meta_frame,
            text=task.status,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        status_label.pack(side="left", padx=(0, 15))
        
        # Due date
        if task.due_date:
            due_text = utils.format_date(task.due_date)
            days_until = utils.get_days_until(task.due_date)
            if days_until < 0:
                due_text += " (Overdue)"
            elif days_until == 0:
                due_text += " (Today)"
            
            due_label = ThemedLabel(
                meta_frame,
                text=f"📅 {due_text}",
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                color_key="fg_secondary"
            )
            due_label.pack(side="left")
        
        # Actions
        actions_frame = ThemedFrame(item, color_key="bg_secondary")
        actions_frame.grid(row=0, column=2, padx=15, pady=15)
        
        ThemedButton(
            actions_frame,
            text="Edit",
            width=60,
            height=32,
            command=lambda: self.edit_task(task)
        ).pack(side="left", padx=2)
        
        ThemedButton(
            actions_frame,
            text="×",
            button_style="danger",
            width=32,
            height=32,
            command=lambda: self.delete_task(task)
        ).pack(side="left", padx=2)
    
    def toggle_task(self, task):
        """Toggle task completion"""
        task.completed = not task.completed
        if task.completed:
            task.completed_at = datetime.now()
            task.status = "Completed"
        else:
            task.completed_at = None
            if task.status == "Completed":
                task.status = "Not Started"
        task.save()
        self.load_tasks()
    
    def show_add_task_dialog(self):
        """Show dialog to add new task"""
        self.show_task_dialog()
    
    def edit_task(self, task):
        """Show dialog to edit task"""
        self.show_task_dialog(task)
    
    def show_task_dialog(self, task=None):
        """Show task add/edit dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task" if task else "New Task")
        dialog.geometry("550x750")
        dialog.transient(self)
        dialog.grab_set()
        
        # Scrollable content
        scroll = ctk.CTkScrollableFrame(
            dialog,
            fg_color=theme_manager.get_color("bg_primary")
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.grid_columnconfigure(0, weight=1)
        
        # Title
        ThemedLabel(scroll, text="Title", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        title_entry = ThemedEntry(scroll, height=40)
        if task:
            title_entry.insert(0, task.title)
        title_entry.pack(fill="x", pady=(0, 20))
        
        # Description
        ThemedLabel(scroll, text="Description", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        desc_text = ThemedTextbox(scroll, height=120)
        if task and task.description:
            desc_text.insert("1.0", task.description)
        desc_text.pack(fill="x", pady=(0, 20))
        
        # Properties row 1
        props1 = ThemedFrame(scroll, color_key="bg_primary")
        props1.pack(fill="x", pady=(0, 20))
        props1.grid_columnconfigure(0, weight=1)
        props1.grid_columnconfigure(1, weight=1)
        
        # Status
        status_frame = ThemedFrame(props1, color_key="bg_primary")
        status_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ThemedLabel(status_frame, text="Status", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        status_combo = ThemedComboBox(status_frame, values=config.TASK_STATUSES, height=40)
        status_combo.set(task.status if task else "Not Started")
        status_combo.pack(fill="x")
        
        # Priority
        priority_frame = ThemedFrame(props1, color_key="bg_primary")
        priority_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ThemedLabel(priority_frame, text="Priority", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        priority_combo = ThemedComboBox(priority_frame, values=config.TASK_PRIORITIES, height=40)
        priority_combo.set(task.priority if task else "Medium")
        priority_combo.pack(fill="x")
        
        # Due date
        ThemedLabel(scroll, text="Due Date", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        due_entry = ThemedEntry(scroll, placeholder_text="YYYY-MM-DD", height=40)
        if task and task.due_date:
            due_entry.insert(0, task.due_date.strftime(config.DATE_FORMAT))
        due_entry.pack(fill="x", pady=(0, 20))
        
        # Tags
        ThemedLabel(scroll, text="Tags", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack(anchor="w", pady=(0, 5))
        tags_entry = ThemedEntry(scroll, placeholder_text="Comma-separated tags", height=40)
        if task and task.tags:
            tags_entry.insert(0, task.tags)
        tags_entry.pack(fill="x", pady=(0, 30))
        
        # Buttons
        btn_frame = ThemedFrame(scroll, color_key="bg_primary")
        btn_frame.pack(fill="x")
        
        def save_task():
            try:
                title_val = title_entry.get().strip()
                if not title_val:
                    return
                
                due_date = None
                if due_entry.get():
                    due_date = datetime.strptime(due_entry.get(), config.DATE_FORMAT)
                
                if task:
                    task.title = title_val
                    task.description = desc_text.get("1.0", "end-1c").strip()
                    task.priority = priority_combo.get()
                    task.status = status_combo.get()
                    task.due_date = due_date
                    task.tags = tags_entry.get().strip() if tags_entry.get().strip() else None
                    task.updated_at = datetime.now()
                    task.save()
                else:
                    Task.create(
                        title=title_val,
                        description=desc_text.get("1.0", "end-1c").strip(),
                        priority=priority_combo.get(),
                        status=status_combo.get(),
                        due_date=due_date,
                        tags=tags_entry.get().strip() if tags_entry.get().strip() else None
                    )
                
                self.load_tasks()
                dialog.destroy()
            except Exception as e:
                print(f"Error saving task: {e}")
        
        ThemedButton(
            btn_frame,
            text="Cancel",
            width=100,
            height=40,
            command=dialog.destroy
        ).pack(side="right", padx=(10, 0))
        
        ThemedButton(
            btn_frame,
            text="Save Task",
            button_style="accent",
            width=120,
            height=40,
            command=save_task
        ).pack(side="right")
    
    def delete_task(self, task):
        """Delete a task"""
        task.delete_instance()
        self.load_tasks()
    
    def on_filter_change(self, value):
        """Handle filter change"""
        self.filter_status = self.status_filter.get()
        self.load_tasks()
    
    def on_sort_change(self, value):
        """Handle sort change"""
        self.sort_by = self.sort_combo.get()
        self.load_tasks()
    
    def refresh(self):
        """Refresh tasks"""
        self.load_tasks()
