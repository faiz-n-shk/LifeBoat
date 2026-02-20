"""
Lifeboat - Config Settings Feature
Manages custom directories for config and database files
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton
from src.core.theme_manager import theme_manager
from src.core.path_manager import path_manager
from src.core import config

class ConfigSettingsSection:
    """Config and database path management section"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.section_frame = None
    
    def create_section(self):
        """Create the config settings section UI"""
        self.section_frame = ThemedFrame(self.parent, color_key="bg_secondary", corner_radius=10)
        self.section_frame.pack(fill="x", pady=(0, 20))
        self.section_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ThemedLabel(
            self.section_frame,
            text="File Locations",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        ThemedLabel(
            self.section_frame,
            text="Customize where your configuration and database files are stored",
            color_key="fg_secondary"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Get current paths info
        paths_info = path_manager.get_current_paths_info()
        
        # Config file section
        self._create_path_section(
            row=2,
            title="Configuration File (config.yaml)",
            current_path=paths_info['config']['current'],
            is_custom=paths_info['config']['is_custom'],
            on_browse=self._browse_config_directory,
            on_reset=self._reset_config_location,
            on_restore=self._restore_default_config
        )
        
        # Separator
        separator = ThemedFrame(self.section_frame, color_key="border", height=1)
        separator.grid(row=3, column=0, sticky="ew", padx=20, pady=15)
        
        # Database file section
        self._create_path_section(
            row=4,
            title="Database File (lifeboat.db)",
            current_path=paths_info['database']['current'],
            is_custom=paths_info['database']['is_custom'],
            on_browse=self._browse_database_directory,
            on_reset=self._reset_database_location,
            on_restore=self._restore_default_database
        )
        
        # Warning message
        warning_frame = ThemedFrame(self.section_frame, color_key="bg_tertiary", corner_radius=6)
        warning_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(15, 20))
        
        ThemedLabel(
            warning_frame,
            text="⚠ Important",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ThemedLabel(
            warning_frame,
            text="• Changing file locations requires restarting the application\n"
                 "• Original files remain in the app directory as backup\n"
                 "• Use 'Restore Defaults' if files become corrupted",
            color_key="fg_secondary",
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        return self.section_frame
    
    def _create_path_section(self, row, title, current_path, is_custom, on_browse, on_reset, on_restore):
        """Create a path configuration section"""
        container = ThemedFrame(self.section_frame, color_key="bg_secondary")
        container.grid(row=row, column=0, sticky="ew", padx=20, pady=5)
        container.grid_columnconfigure(0, weight=1)
        
        # Title
        ThemedLabel(
            container,
            text=title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Current path display
        path_frame = ThemedFrame(container, color_key="bg_tertiary", corner_radius=6)
        path_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        path_frame.grid_columnconfigure(0, weight=1)
        
        status_text = "Custom Location" if is_custom else "Default Location"
        status_color = "accent" if is_custom else "fg_secondary"
        
        ThemedLabel(
            path_frame,
            text=status_text,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL)
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        
        path_label = ThemedLabel(
            path_frame,
            text=current_path,
            color_key="fg_secondary",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL)
        )
        path_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        
        # Buttons
        btn_frame = ThemedFrame(container, color_key="bg_secondary")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        ThemedButton(
            btn_frame,
            text="Browse...",
            width=100,
            command=on_browse
        ).pack(side="left", padx=(0, 5))
        
        if is_custom:
            ThemedButton(
                btn_frame,
                text="Reset to Default",
                width=120,
                command=on_reset
            ).pack(side="left", padx=5)
        
        ThemedButton(
            btn_frame,
            text="Restore Defaults",
            button_style="warning",
            width=130,
            command=on_restore
        ).pack(side="left", padx=5)
    
    def _browse_config_directory(self):
        """Browse for custom config directory"""
        directory = filedialog.askdirectory(
            title="Select Directory for Config File",
            mustexist=False
        )
        
        if directory:
            success, message = path_manager.set_custom_config_path(directory)
            if success:
                messagebox.showinfo(
                    "Success",
                    f"{message}\n\nPlease restart the application for changes to take effect."
                )
                self._refresh_section()
            else:
                messagebox.showerror("Error", message)
    
    def _browse_database_directory(self):
        """Browse for custom database directory"""
        directory = filedialog.askdirectory(
            title="Select Directory for Database File",
            mustexist=False
        )
        
        if directory:
            success, message = path_manager.set_custom_database_path(directory)
            if success:
                messagebox.showinfo(
                    "Success",
                    f"{message}\n\nPlease restart the application for changes to take effect."
                )
                self._refresh_section()
            else:
                messagebox.showerror("Error", message)
    
    def _reset_config_location(self):
        """Reset config to default location"""
        if messagebox.askyesno(
            "Confirm Reset",
            "Reset config file to default location?\n\n"
            "Your custom config file will remain in its current location.\n"
            "The app will use the default config after restart."
        ):
            success, message = path_manager.reset_config_to_default()
            if success:
                messagebox.showinfo(
                    "Success",
                    f"{message}\n\nPlease restart the application."
                )
                self._refresh_section()
            else:
                messagebox.showerror("Error", message)
    
    def _reset_database_location(self):
        """Reset database to default location"""
        if messagebox.askyesno(
            "Confirm Reset",
            "Reset database file to default location?\n\n"
            "Your custom database file will remain in its current location.\n"
            "The app will use the default database after restart."
        ):
            success, message = path_manager.reset_database_to_default()
            if success:
                messagebox.showinfo(
                    "Success",
                    f"{message}\n\nPlease restart the application."
                )
                self._refresh_section()
            else:
                messagebox.showerror("Error", message)
    
    def _restore_default_config(self):
        """Restore config to default settings"""
        if messagebox.askyesno(
            "Confirm Restore",
            "Restore config file to default settings?\n\n"
            "This will overwrite your current config with default values.\n"
            "Your themes and other data will not be affected.\n\n"
            "This action cannot be undone!"
        ):
            success, message = path_manager.restore_default_config()
            if success:
                messagebox.showinfo(
                    "Success",
                    f"{message}\n\nPlease restart the application to load default settings."
                )
            else:
                messagebox.showerror("Error", message)
    
    def _restore_default_database(self):
        """Restore database to default state"""
        if messagebox.askyesno(
            "Confirm Restore",
            "Restore database to default state?\n\n"
            "⚠ WARNING: This will DELETE all your data!\n"
            "• All tasks, notes, habits, expenses will be lost\n"
            "• A backup will be created automatically\n\n"
            "This action cannot be undone!\n\n"
            "Are you absolutely sure?"
        ):
            # Double confirmation for database restore
            if messagebox.askyesno(
                "Final Confirmation",
                "This is your last chance!\n\n"
                "Restore database and DELETE ALL DATA?"
            ):
                success, message = path_manager.restore_default_database()
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"{message}\n\nPlease restart the application."
                    )
                else:
                    messagebox.showerror("Error", message)
    
    def _refresh_section(self):
        """Refresh the section to show updated paths"""
        if self.section_frame:
            self.section_frame.destroy()
        self.create_section()
