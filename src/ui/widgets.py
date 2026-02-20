"""
Lifeboat - Custom Widgets
Reusable custom widgets for the application
"""
import customtkinter as ctk
from src.core.theme_manager import theme_manager
from tkinter import colorchooser
from src.core import config

class ThemedFrame(ctk.CTkFrame):
    """Frame with theme support"""
    def __init__(self, master, color_key="bg_secondary", corner_radius=None, **kwargs):
        self.color_key = color_key
        # Use smaller corner radius for better performance
        if corner_radius is None:
            corner_radius = 6
        super().__init__(
            master,
            fg_color=theme_manager.get_color(color_key),
            corner_radius=corner_radius,
            **kwargs
        )
    
    def update_theme(self):
        self.configure(fg_color=theme_manager.get_color(self.color_key))

class ThemedButton(ctk.CTkButton):
    """Button with theme support"""
    def __init__(self, master, button_style="accent", **kwargs):
        self.button_style = button_style
        colors = self._get_colors()
        super().__init__(
            master,
            fg_color=colors['fg'],
            hover_color=colors['hover'],
            text_color=colors['text'],
            **kwargs
        )
    
    def _get_colors(self):
        if self.button_style == "accent":
            return {
                'fg': theme_manager.get_color('accent'),
                'hover': theme_manager.get_color('accent_hover'),
                'text': "#ffffff"
            }
        elif self.button_style == "success":
            return {
                'fg': theme_manager.get_color('success'),
                'hover': theme_manager.get_color('success'),
                'text': "#ffffff"
            }
        elif self.button_style == "danger":
            return {
                'fg': theme_manager.get_color('danger'),
                'hover': theme_manager.get_color('danger'),
                'text': "#ffffff"
            }
        else:
            # Default button style - use theme colors
            return {
                'fg': theme_manager.get_color('bg_tertiary'),
                'hover': theme_manager.get_color('border'),
                'text': theme_manager.get_color('fg_primary')
            }
    
    def update_theme(self):
        colors = self._get_colors()
        self.configure(
            fg_color=colors['fg'],
            hover_color=colors['hover'],
            text_color=colors['text']
        )

class ThemedLabel(ctk.CTkLabel):
    """Label with theme support"""
    def __init__(self, master, color_key="fg_primary", **kwargs):
        self.color_key = color_key
        super().__init__(
            master,
            text_color=theme_manager.get_color(color_key),
            **kwargs
        )
    
    def update_theme(self):
        self.configure(text_color=theme_manager.get_color(self.color_key))

class ThemedEntry(ctk.CTkEntry):
    """Entry with theme support"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            text_color=theme_manager.get_color('fg_primary'),
            **kwargs
        )
    
    def update_theme(self):
        self.configure(
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            text_color=theme_manager.get_color('fg_primary')
        )

class ThemedTextbox(ctk.CTkTextbox):
    """Textbox with theme support"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            text_color=theme_manager.get_color('fg_primary'),
            **kwargs
        )
        # Fix black background in text area
        self._textbox.configure(
            bg=theme_manager.get_color('bg_tertiary'),
            fg=theme_manager.get_color('fg_primary'),
            insertbackground=theme_manager.get_color('fg_primary'),
            selectbackground=theme_manager.get_color('accent'),
            selectforeground="#ffffff"
        )
    
    def update_theme(self):
        self.configure(
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            text_color=theme_manager.get_color('fg_primary')
        )
        # Update internal textbox colors
        self._textbox.configure(
            bg=theme_manager.get_color('bg_tertiary'),
            fg=theme_manager.get_color('fg_primary'),
            insertbackground=theme_manager.get_color('fg_primary'),
            selectbackground=theme_manager.get_color('accent'),
            selectforeground="#ffffff"
        )

class ThemedComboBox(ctk.CTkComboBox):
    """ComboBox with theme support"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            button_color=theme_manager.get_color('accent'),
            button_hover_color=theme_manager.get_color('accent_hover'),
            text_color=theme_manager.get_color('fg_primary'),
            **kwargs
        )
    
    def update_theme(self):
        self.configure(
            fg_color=theme_manager.get_color('bg_tertiary'),
            border_color=theme_manager.get_color('border'),
            button_color=theme_manager.get_color('accent'),
            button_hover_color=theme_manager.get_color('accent_hover'),
            text_color=theme_manager.get_color('fg_primary')
        )

class ColorPickerButton(ctk.CTkButton):
    """Button that opens color picker"""
    def __init__(self, master, initial_color="#000000", callback=None, **kwargs):
        self.current_color = initial_color
        self.callback = callback
        super().__init__(
            master,
            text="",
            width=40,
            height=30,
            fg_color=initial_color,
            hover_color=initial_color,
            command=self.pick_color,
            **kwargs
        )
    
    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)[1]
        if color:
            self.current_color = color
            self.configure(fg_color=color, hover_color=color)
            if self.callback:
                self.callback(color)
    
    def get_color(self):
        return self.current_color
    
    def set_color(self, color):
        self.current_color = color
        self.configure(fg_color=color, hover_color=color)

class StatCard(ThemedFrame):
    """Card widget for displaying statistics"""
    def __init__(self, master, title, value, icon=None, color="accent", **kwargs):
        super().__init__(master, color_key="bg_tertiary", **kwargs)
        
        self.configure(corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ThemedLabel(
            self,
            text=title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.value_label = ThemedLabel(
            self,
            text=str(value),
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        self.value_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
    
    def update_value(self, value):
        self.value_label.configure(text=str(value))

class SearchBar(ThemedFrame):
    """Search bar widget"""
    def __init__(self, master, placeholder="Search...", callback=None, **kwargs):
        super().__init__(master, color_key="bg_secondary", **kwargs)
        
        self.callback = callback
        self.configure(corner_radius=20, height=40)
        
        self.entry = ThemedEntry(
            self,
            placeholder_text=placeholder,
            corner_radius=20,
            height=40
        )
        self.entry.pack(fill="both", expand=True, padx=2, pady=2)
        self.entry.bind("<Return>", lambda e: self._on_search())
        self.entry.bind("<KeyRelease>", lambda e: self._on_search())
    
    def _on_search(self):
        if self.callback:
            self.callback(self.entry.get())
    
    def get_text(self):
        return self.entry.get()
    
    def clear(self):
        self.entry.delete(0, "end")
