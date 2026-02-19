"""
Lifeboat - Theme Manager
Handles theme creation, editing, and application
"""
import customtkinter as ctk
from src.core.config import DEFAULT_THEMES

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.current_theme = None
        self._callbacks = []
    
    def register_callback(self, callback):
        """Register a callback to be called when theme changes"""
        self._callbacks.append(callback)
    
    def load_active_theme(self):
        """Load the currently active theme"""
        from src.core.database import get_active_theme
        try:
            self.current_theme = get_active_theme()
        except:
            self.current_theme = None
        return self.current_theme
    
    def get_color(self, color_key):
        """Get a color value from current theme"""
        if not self.current_theme:
            default_colors = DEFAULT_THEMES.get("Dark", {})
            return default_colors.get(color_key, "#000000")
        return getattr(self.current_theme, color_key, "#000000")
    
    def apply_theme(self, theme_name):
        """Apply a theme to the application"""
        from src.core.database import set_active_theme
        self.current_theme = set_active_theme(theme_name)
        
        if theme_name == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
        
        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback()
            except:
                pass
        
        return self.current_theme
    
    def create_custom_theme(self, colors, base_theme_name=None):
        """Create a new custom theme"""
        from src.core.database import Theme
        custom_count = Theme.select().where(Theme.is_custom == True).count()
        theme_name = f"CustomTheme-{custom_count + 1}"
        
        theme = Theme.create(
            name=theme_name,
            is_custom=True,
            **colors
        )
        
        return theme
    
    def update_theme(self, theme_name, colors):
        """Update an existing theme"""
        from src.core.database import Theme
        theme = Theme.get(Theme.name == theme_name)
        
        if not theme.is_custom:
            return self.create_custom_theme(colors, theme_name)
        
        for key, value in colors.items():
            setattr(theme, key, value)
        theme.save()
        
        return theme
    
    def delete_theme(self, theme_name):
        """Delete a custom theme"""
        from src.core.database import Theme
        theme = Theme.get(Theme.name == theme_name)
        if theme.is_custom:
            theme.delete_instance()
            return True
        return False
    
    def get_all_themes(self):
        """Get all available themes"""
        from src.core.database import Theme
        return list(Theme.select().order_by(Theme.is_custom, Theme.name))
    
    def export_theme(self, theme_name):
        """Export theme as dictionary"""
        from src.core.database import Theme
        theme = Theme.get(Theme.name == theme_name)
        return {
            'name': theme.name,
            'bg_primary': theme.bg_primary,
            'bg_secondary': theme.bg_secondary,
            'bg_tertiary': theme.bg_tertiary,
            'fg_primary': theme.fg_primary,
            'fg_secondary': theme.fg_secondary,
            'accent': theme.accent,
            'accent_hover': theme.accent_hover,
            'success': theme.success,
            'warning': theme.warning,
            'danger': theme.danger,
            'border': theme.border
        }

# Global theme manager instance
theme_manager = ThemeManager()
