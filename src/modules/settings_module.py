"""
Lifeboat - Settings Module
Settings and options for application
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ColorPickerButton
from src.core.theme_manager import theme_manager
from src.core.database import Theme, Settings, db
from src.core import config

class SettingsModule(ThemedFrame):
    """Settings and customization module"""
    
    def __init__(self, master, app_instance=None, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.app_instance = app_instance
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title = ThemedLabel(
            header,
            text="Settings",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.pack(side="left")
        
        # Content
        content = ctk.CTkScrollableFrame(
            self,
            fg_color=theme_manager.get_color("bg_primary")
        )
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content.grid_columnconfigure(0, weight=1)
        
        # Theme section
        theme_section = ThemedFrame(content, color_key="bg_secondary", corner_radius=10)
        theme_section.pack(fill="x", pady=(0, 20))
        theme_section.grid_columnconfigure(0, weight=1)
        
        ThemedLabel(
            theme_section,
            text="Theme",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        ThemedLabel(
            theme_section,
            text="Select a theme or create your own custom theme",
            color_key="fg_secondary"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Theme list
        self.theme_list_frame = ThemedFrame(theme_section, color_key="bg_secondary")
        self.theme_list_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        self.load_themes()
        
        # Create custom theme button
        ThemedButton(
            theme_section,
            text="+ Create Custom Theme",
            button_style="accent",
            command=self.show_theme_editor
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 20))
        
        # App info section
        info_section = ThemedFrame(content, color_key="bg_secondary", corner_radius=10)
        info_section.pack(fill="x", pady=(0, 20))
        
        ThemedLabel(
            info_section,
            text="About",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        ThemedLabel(
            info_section,
            text=f"{config.APP_NAME} v{config.APP_VERSION}",
            color_key="fg_secondary"
        ).pack(anchor="w", padx=20, pady=5)
        
        ThemedLabel(
            info_section,
            text="A comprehensive personal life management application",
            color_key="fg_secondary"
        ).pack(anchor="w", padx=20, pady=(0, 20))
    
    def load_themes(self):
        """Load available themes"""
        for widget in self.theme_list_frame.winfo_children():
            widget.destroy()
        
        themes = theme_manager.get_all_themes()
        current_theme = theme_manager.current_theme
        
        if not current_theme:
            theme_manager.load_active_theme()
            current_theme = theme_manager.current_theme
        
        for theme in themes:
            theme_item = ThemedFrame(self.theme_list_frame, color_key="bg_tertiary", corner_radius=8)
            theme_item.pack(fill="x", pady=5)
            theme_item.grid_columnconfigure(1, weight=1)
            
            # Color preview
            preview_frame = ThemedFrame(theme_item, color_key="bg_tertiary")
            preview_frame.grid(row=0, column=0, padx=15, pady=10)
            
            colors = [theme.bg_primary, theme.accent, theme.success, theme.warning, theme.danger]
            for i, color in enumerate(colors):
                color_box = ThemedFrame(preview_frame, corner_radius=3)
                color_box.configure(fg_color=color, width=20, height=20)
                color_box.pack(side="left", padx=2)
            
            # Theme name
            name_frame = ThemedFrame(theme_item, color_key="bg_tertiary")
            name_frame.grid(row=0, column=1, sticky="w", padx=10, pady=10)
            
            name_label = ThemedLabel(
                name_frame,
                text=theme.name,
                font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
            )
            name_label.pack(anchor="w")
            
            if theme.is_custom:
                custom_label = ThemedLabel(
                    name_frame,
                    text="Custom Theme",
                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                    color_key="fg_secondary"
                )
                custom_label.pack(anchor="w")
            
            # Actions
            actions_frame = ThemedFrame(theme_item, color_key="bg_tertiary")
            actions_frame.grid(row=0, column=2, padx=15, pady=10)
            
            if theme.name == current_theme.name:
                active_label = ThemedLabel(
                    actions_frame,
                    text="✓ Active",
                    font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
                )
                active_label.configure(text_color=theme_manager.get_color("success"))
                active_label.pack(side="left", padx=5)
            else:
                ThemedButton(
                    actions_frame,
                    text="Apply",
                    width=80,
                    command=lambda t=theme: self.apply_theme(t)
                ).pack(side="left", padx=2)
            
            if theme.is_custom:
                ThemedButton(
                    actions_frame,
                    text="Edit",
                    width=60,
                    command=lambda t=theme: self.show_theme_editor(t)
                ).pack(side="left", padx=2)
                
                ThemedButton(
                    actions_frame,
                    text="Delete",
                    button_style="danger",
                    width=60,
                    command=lambda t=theme: self.delete_theme(t)
                ).pack(side="left", padx=2)
            else:
                ThemedButton(
                    actions_frame,
                    text="Customize",
                    width=100,
                    command=lambda t=theme: self.show_theme_editor(t)
                ).pack(side="left", padx=2)
    
    def apply_theme(self, theme):
        """Apply a theme"""
        theme_manager.apply_theme(theme.name)
        if self.app_instance:
            self.app_instance.on_theme_change()
        self.load_themes()
    
    def show_theme_editor(self, base_theme=None):
        """Show theme editor dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Theme Editor")
        dialog.geometry("500x700")
        dialog.transient(self)
        dialog.grab_set()
        
        content = ThemedFrame(dialog, color_key="bg_primary")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        if base_theme:
            ThemedLabel(
                content,
                text=f"Editing: {base_theme.name}",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
            ).pack(pady=(0, 20))
        else:
            ThemedLabel(
                content,
                text="Create Custom Theme",
                font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
            ).pack(pady=(0, 20))
        
        # Color pickers
        color_fields = [
            ("bg_primary", "Background Primary"),
            ("bg_secondary", "Background Secondary"),
            ("bg_tertiary", "Background Tertiary"),
            ("fg_primary", "Text Primary"),
            ("fg_secondary", "Text Secondary"),
            ("accent", "Accent Color"),
            ("accent_hover", "Accent Hover"),
            ("success", "Success Color"),
            ("warning", "Warning Color"),
            ("danger", "Danger Color"),
            ("border", "Border Color")
        ]
        
        color_pickers = {}
        
        for field, label in color_fields:
            row = ThemedFrame(content, color_key="bg_primary")
            row.pack(fill="x", pady=5)
            
            ThemedLabel(row, text=label, width=150).pack(side="left")
            
            initial_color = getattr(base_theme, field) if base_theme else "#000000"
            picker = ColorPickerButton(row, initial_color=initial_color)
            picker.pack(side="left", padx=10)
            
            color_pickers[field] = picker
        
        # Buttons
        btn_frame = ThemedFrame(content, color_key="bg_primary")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_theme():
            colors = {field: picker.get_color() for field, picker in color_pickers.items()}
            
            if base_theme and not base_theme.is_custom:
                # Creating custom from default
                new_theme = theme_manager.create_custom_theme(colors)
            elif base_theme:
                # Updating custom theme
                theme_manager.update_theme(base_theme.name, colors)
            else:
                # Creating new custom theme
                new_theme = theme_manager.create_custom_theme(colors)
            
            self.load_themes()
            dialog.destroy()
        
        ThemedButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ThemedButton(btn_frame, text="Save", button_style="accent", command=save_theme).pack(side="right")
    
    def delete_theme(self, theme):
        """Delete a custom theme"""
        if theme_manager.delete_theme(theme.name):
            self.load_themes()
    
    def refresh(self):
        """Refresh settings"""
        self.load_themes()
