"""
Lifeboat - Main Application
"""
import customtkinter as ctk
from src.core import config
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton
from src.core.theme_manager import theme_manager

class LifeboatApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration - do this FIRST for instant visibility
        self.title(config.APP_NAME)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Set basic theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Show loading screen
        self.show_loading_screen()
        
        # Schedule initialization after window is visible
        self.after(10, self.initialize_app)
    
    def show_loading_screen(self):
        """simple loading screen with boat logo and app name"""
        loading_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        loading_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="⛵ " + config.APP_NAME,
            font=(config.FONT_FAMILY, 32, "bold"),
            text_color="#ffffff"
        ).pack(expand=True)
        
        self.loading_frame = loading_frame
    
    def initialize_app(self):
        """Initialize app after window is visible"""
        # Import and initialize database
        from src.core.database import initialize_database
        initialize_database()
        
        # Load active theme
        theme_manager.load_active_theme()
        
        # Register theme change callback
        theme_manager.register_callback(self.on_theme_change)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Current module
        self.current_module = None
        self.current_module_name = None
        
        # Remove loading screen
        self.loading_frame.destroy()
        
        # Setup UI
        self.setup_ui()
        
        # Load dashboard
        self.show_module("Dashboard")
    
    def setup_ui(self):
        """Setup main UI"""
        # Sidebar
        self.sidebar = ThemedFrame(self, color_key="bg_secondary", width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(10, weight=1)  # Changed from 8 to 10
        
        # Logo/Title
        logo_frame = ThemedFrame(self.sidebar, color_key="bg_secondary")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=30)
        
        app_title = ThemedLabel(
            logo_frame,
            text="⛵ " + config.APP_NAME,
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        app_title.pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "📊"),
            ("Calendar", "📅"),
            ("Tasks", "✓"),
            ("Todo", "☑"),
            ("Expenses", "💰"),
            ("Goals", "🎯"),
            ("Notes", "📝"),
            ("Habits", "🔄"),
            ("Settings", "⚙")
        ]
        
        for i, (name, icon) in enumerate(nav_items):
            btn = ThemedButton(
                self.sidebar,
                text=f"{icon}  {name}",
                width=210,
                height=45,
                anchor="w",
                command=lambda n=name: self.show_module(n),
                button_style="default"  # Use default style for nav buttons
            )
            btn.grid(row=i+1, column=0, padx=20, pady=5)
            self.nav_buttons[name] = btn
        
        # Footer - moved to row 11 to be below all buttons
        footer = ThemedFrame(self.sidebar, color_key="bg_secondary")
        footer.grid(row=11, column=0, sticky="ew", padx=20, pady=20)
        
        version_label = ThemedLabel(
            footer,
            text=f"v{config.APP_VERSION}",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        version_label.pack()
        
        # Main content area
        self.content_frame = ThemedFrame(self, color_key="bg_primary")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def show_module(self, module_name):
        """Show a specific module"""
        # Don't reload if already showing
        if self.current_module_name == module_name and self.current_module:
            return
        
        # Clear current module
        if self.current_module:
            self.current_module.destroy()
        
        # Update navigation buttons
        for name, btn in self.nav_buttons.items():
            if name == module_name:
                btn.configure(
                    fg_color=theme_manager.get_color("accent"),
                    hover_color=theme_manager.get_color("accent_hover"),
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color=theme_manager.get_color("bg_tertiary"),
                    hover_color=theme_manager.get_color("border"),
                    text_color=theme_manager.get_color("fg_primary")
                )
        
        # Lazy import and create module
        if module_name == "Dashboard":
            from src.modules.dashboard import DashboardModule
            self.current_module = DashboardModule(self.content_frame)
        elif module_name == "Calendar":
            from src.modules.calendar_module import CalendarModule
            self.current_module = CalendarModule(self.content_frame)
        elif module_name == "Tasks":
            from src.modules.tasks_module import TasksModule
            self.current_module = TasksModule(self.content_frame)
        elif module_name == "Todo":
            from src.modules.todo_module import TodoModule
            self.current_module = TodoModule(self.content_frame)
        elif module_name == "Expenses":
            from src.modules.expenses_module import ExpensesModule
            self.current_module = ExpensesModule(self.content_frame)
        elif module_name == "Goals":
            from src.modules.goals_module import GoalsModule
            self.current_module = GoalsModule(self.content_frame)
        elif module_name == "Notes":
            from src.modules.notes_module import NotesModule
            self.current_module = NotesModule(self.content_frame)
        elif module_name == "Habits":
            from src.modules.habits_module import HabitsModule
            self.current_module = HabitsModule(self.content_frame)
        elif module_name == "Settings":
            from src.modules.settings_module import SettingsModule
            self.current_module = SettingsModule(self.content_frame, app_instance=self)
        
        self.current_module.grid(row=0, column=0, sticky="nsew")
        self.current_module_name = module_name
    
    def on_theme_change(self):
        """Handle theme change - use after_idle to prevent freezing"""
        self.after_idle(self._apply_theme_changes)
    
    def _apply_theme_changes(self):
        """Apply theme changes to all widgets"""
        # Update main window
        self.configure(fg_color=theme_manager.get_color("bg_primary"))
        
        # Update sidebar and content frame
        self.sidebar.update_theme()
        self.content_frame.update_theme()
        
        # Update all themed widgets recursively first
        self._update_widget_theme(self)
        
        # Then update navigation buttons with proper states
        for name, btn in self.nav_buttons.items():
            if name == self.current_module_name:
                # Active button - use accent color with white text
                btn.configure(
                    fg_color=theme_manager.get_color("accent"),
                    hover_color=theme_manager.get_color("accent_hover"),
                    text_color="#ffffff"
                )
            else:
                # Inactive button - use tertiary background with primary text
                btn.configure(
                    fg_color=theme_manager.get_color("bg_tertiary"),
                    hover_color=theme_manager.get_color("border"),
                    text_color=theme_manager.get_color("fg_primary")
                )
        
        # Refresh current module
        if self.current_module and hasattr(self.current_module, 'refresh'):
            self.current_module.refresh()
    
    def _update_widget_theme(self, widget):
        """Recursively update theme for all widgets"""
        if hasattr(widget, 'update_theme'):
            try:
                widget.update_theme()
            except:
                pass
        
        for child in widget.winfo_children():
            self._update_widget_theme(child)
