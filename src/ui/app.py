"""
Lifeboat - Main Application
"""
import customtkinter as ctk
from src.core import config
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton
from src.core.theme_manager import theme_manager
import sys
import os

# Performance optimizations for Windows
if sys.platform == "win32":
    try:
        # Enable high DPI awareness
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass

# Optimize CustomTkinter rendering
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# Reduce corner radius for better performance
ctk.set_default_color_theme("blue")

class LifeboatApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Performance optimizations
        self._theme_update_id = None
        
        # Window configuration - do this FIRST for instant visibility
        self.title(config.APP_NAME)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Set basic theme
        ctk.set_appearance_mode("dark")
        
        # Optimize Tkinter rendering
        try:
            # Reduce update frequency for smoother resize
            self.tk.call('wm', 'attributes', '.', '-alpha', 0.0)
            self.update()
            self.tk.call('wm', 'attributes', '.', '-alpha', 1.0)
        except:
            pass
        
        # Show loading screen
        self.show_loading_screen()
        
        # Schedule initialization after window is visible
        self.after(10, self.initialize_app)
    
    def show_loading_screen(self):
        """Show a simple loading screen"""
        loading_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        loading_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="⛵ " + config.APP_NAME,
            font=(config.FONT_FAMILY, 32, "bold"),
            text_color="#ffffff"
        ).pack(expand=True)
        
        self.loading_frame = loading_frame
        self.update()  # Force update to show loading screen
    
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
            self.current_module = None
        
        # Update navigation buttons immediately
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
        
        # Force update to prevent lag
        self.update_idletasks()
        
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
        
        if self.current_module:
            self.current_module.grid(row=0, column=0, sticky="nsew")
        
        self.current_module_name = module_name
    
    def on_theme_change(self):
        """Handle theme change - use after_idle to prevent freezing"""
        # Cancel any pending theme updates
        if hasattr(self, '_theme_update_id') and self._theme_update_id is not None:
            try:
                self.after_cancel(self._theme_update_id)
            except:
                pass
        
        # Schedule theme update
        self._theme_update_id = self.after_idle(self._apply_theme_changes)
    
    def _apply_theme_changes(self):
        """Apply theme changes to all widgets"""
        # Update main window
        self.configure(fg_color=theme_manager.get_color("bg_primary"))
        
        # Update sidebar and content frame
        self.sidebar.configure(fg_color=theme_manager.get_color("bg_secondary"))
        self.content_frame.configure(fg_color=theme_manager.get_color("bg_primary"))
        
        # Update navigation buttons with proper states
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
        
        # Force update current module by reloading it
        if self.current_module and self.current_module_name:
            # Save current module name
            current = self.current_module_name
            # Destroy current module
            self.current_module.destroy()
            self.current_module = None
            self.current_module_name = None
            # Reload it with new theme
            self.show_module(current)
    
    def _update_widget_theme(self, widget):
        """Recursively update theme for all widgets - REMOVED FOR PERFORMANCE"""
        # This method is no longer used to prevent lag
        pass
    
    def refresh_all_modules(self):
        """Refresh all modules to apply config changes"""
        # Reload current module to apply changes
        if self.current_module and self.current_module_name:
            current = self.current_module_name
            self.current_module.destroy()
            self.current_module = None
            self.current_module_name = None
            self.show_module(current)
