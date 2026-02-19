"""
Lifeboat - Goals Module
Goals tracking and management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, ThemedComboBox
from src.core.theme_manager import theme_manager
from src.core.database import Goal, db
from datetime import datetime
from src.core import config
from src.utils import helpers as utils

class GoalsModule(ThemedFrame):
    """Goals tracking module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_goals()
    
    def setup_ui(self):
        """Setup goals UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title = ThemedLabel(
            header,
            text="Goals",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.pack(side="left")
        
        ThemedButton(
            header,
            text="+ Add Goal",
            button_style="accent",
            command=self.show_add_goal_dialog
        ).pack(side="right")
        
        # Goals list
        self.goals_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=theme_manager.get_color("bg_primary")
        )
        self.goals_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.goals_scroll.grid_columnconfigure(0, weight=1)
    
    def load_goals(self):
        """Load and display goals"""
        for widget in self.goals_scroll.winfo_children():
            widget.destroy()
        
        goals = list(Goal.select().order_by(Goal.completed, Goal.target_date))
        
        if not goals:
            no_goals = ThemedLabel(
                self.goals_scroll,
                text="No goals yet. Create one to get started!",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE),
                color_key="fg_secondary"
            )
            no_goals.pack(pady=50)
            return
        
        for goal in goals:
            self.create_goal_widget(goal)
    
    def create_goal_widget(self, goal):
        """Create goal widget"""
        goal_frame = ThemedFrame(self.goals_scroll, color_key="bg_secondary", corner_radius=10)
        goal_frame.pack(fill="x", pady=10, padx=5)
        goal_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ThemedFrame(goal_frame, color_key="bg_secondary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        title = ThemedLabel(
            header,
            text=goal.title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        title.pack(side="left")
        
        if goal.completed:
            status = ThemedLabel(
                header,
                text="✓ Completed",
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
            )
            status.configure(text_color=theme_manager.get_color("success"))
            status.pack(side="right")
        
        # Description
        if goal.description:
            desc = ThemedLabel(
                goal_frame,
                text=goal.description,
                color_key="fg_secondary",
                wraplength=800
            )
            desc.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Progress bar
        progress_frame = ThemedFrame(goal_frame, color_key="bg_secondary")
        progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        progress_bg = ThemedFrame(progress_frame, color_key="bg_tertiary", height=30, corner_radius=15)
        progress_bg.pack(fill="x")
        
        if goal.progress > 0:
            progress_fill = ThemedFrame(
                progress_bg,
                color_key="accent",
                height=30,
                corner_radius=15
            )
            progress_fill.configure(fg_color=theme_manager.get_color("success") if goal.completed else theme_manager.get_color("accent"))
            progress_fill.place(relwidth=goal.progress/100, relheight=1)
        
        progress_label = ThemedLabel(
            progress_bg,
            text=f"{goal.progress}%",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        )
        progress_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Metadata
        meta_frame = ThemedFrame(goal_frame, color_key="bg_secondary")
        meta_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        if goal.category:
            cat_label = ThemedLabel(
                meta_frame,
                text=f"📁 {goal.category}",
                color_key="fg_secondary"
            )
            cat_label.pack(side="left", padx=(0, 20))
        
        if goal.target_date:
            days_left = utils.get_days_until(goal.target_date)
            date_text = f"🎯 {utils.format_date(goal.target_date)}"
            if not goal.completed:
                if days_left < 0:
                    date_text += " (Overdue)"
                elif days_left == 0:
                    date_text += " (Today)"
                elif days_left <= 7:
                    date_text += f" ({days_left} days left)"
            
            date_label = ThemedLabel(
                meta_frame,
                text=date_text,
                color_key="fg_secondary"
            )
            date_label.pack(side="left")
        
        # Actions
        actions = ThemedFrame(goal_frame, color_key="bg_secondary")
        actions.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        ThemedButton(
            actions,
            text="Update Progress",
            width=140,
            command=lambda: self.update_progress(goal)
        ).pack(side="left", padx=(0, 5))
        
        ThemedButton(
            actions,
            text="Edit",
            width=80,
            command=lambda: self.edit_goal(goal)
        ).pack(side="left", padx=5)
        
        if not goal.completed:
            ThemedButton(
                actions,
                text="Mark Complete",
                button_style="success",
                width=120,
                command=lambda: self.complete_goal(goal)
            ).pack(side="left", padx=5)
        
        ThemedButton(
            actions,
            text="Delete",
            button_style="danger",
            width=80,
            command=lambda: self.delete_goal(goal)
        ).pack(side="right")
    
    def show_add_goal_dialog(self):
        """Show add goal dialog"""
        self.show_goal_dialog()
    
    def edit_goal(self, goal):
        """Edit goal"""
        self.show_goal_dialog(goal)
    
    def show_goal_dialog(self, goal=None):
        """Show goal dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Goal" if goal else "Add Goal")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        content = ThemedFrame(dialog, color_key="bg_primary")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ThemedLabel(content, text="Goal Title:").pack(anchor="w", pady=(0, 5))
        title_entry = ThemedEntry(content)
        if goal:
            title_entry.insert(0, goal.title)
        title_entry.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Description:").pack(anchor="w", pady=(0, 5))
        desc_text = ThemedTextbox(content, height=100)
        if goal and goal.description:
            desc_text.insert("1.0", goal.description)
        desc_text.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Category:").pack(anchor="w", pady=(0, 5))
        category_entry = ThemedEntry(content)
        if goal and goal.category:
            category_entry.insert(0, goal.category)
        category_entry.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Target Date (YYYY-MM-DD):").pack(anchor="w", pady=(0, 5))
        date_entry = ThemedEntry(content)
        if goal and goal.target_date:
            date_entry.insert(0, goal.target_date.strftime(config.DATE_FORMAT))
        date_entry.pack(fill="x", pady=(0, 15))
        
        ThemedLabel(content, text="Progress (0-100):").pack(anchor="w", pady=(0, 5))
        progress_entry = ThemedEntry(content)
        progress_entry.insert(0, str(goal.progress) if goal else "0")
        progress_entry.pack(fill="x", pady=(0, 15))
        
        btn_frame = ThemedFrame(content, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_goal():
            try:
                target_date = None
                if date_entry.get():
                    target_date = datetime.strptime(date_entry.get(), config.DATE_FORMAT).date()
                
                progress = int(progress_entry.get())
                
                if goal:
                    goal.title = title_entry.get()
                    goal.description = desc_text.get("1.0", "end-1c")
                    goal.category = category_entry.get() if category_entry.get() else None
                    goal.target_date = target_date
                    goal.progress = progress
                    goal.updated_at = datetime.now()
                    goal.save()
                else:
                    Goal.create(
                        title=title_entry.get(),
                        description=desc_text.get("1.0", "end-1c"),
                        category=category_entry.get() if category_entry.get() else None,
                        target_date=target_date,
                        progress=progress
                    )
                
                self.load_goals()
                dialog.destroy()
            except Exception as e:
                print(f"Error saving goal: {e}")
        
        ThemedButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save", button_style="accent", command=save_goal).pack(side="right")
    
    def update_progress(self, goal):
        """Update goal progress"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Progress")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        
        content = ThemedFrame(dialog, color_key="bg_primary")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ThemedLabel(content, text=f"Progress for: {goal.title}").pack(pady=(0, 15))
        
        ThemedLabel(content, text="Progress (0-100):").pack(anchor="w", pady=(0, 5))
        progress_entry = ThemedEntry(content)
        progress_entry.insert(0, str(goal.progress))
        progress_entry.pack(fill="x", pady=(0, 15))
        
        btn_frame = ThemedFrame(content, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_progress():
            try:
                progress = int(progress_entry.get())
                goal.progress = min(100, max(0, progress))
                if goal.progress == 100:
                    goal.completed = True
                goal.updated_at = datetime.now()
                goal.save()
                self.load_goals()
                dialog.destroy()
            except:
                pass
        
        ThemedButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save", button_style="accent", command=save_progress).pack(side="right")
    
    def complete_goal(self, goal):
        """Mark goal as complete"""
        goal.completed = True
        goal.progress = 100
        goal.updated_at = datetime.now()
        goal.save()
        self.load_goals()
    
    def delete_goal(self, goal):
        """Delete goal"""
        goal.delete_instance()
        self.load_goals()
    
    def refresh(self):
        """Refresh goals"""
        self.load_goals()
