"""
Lifeboat - Locale Settings Feature
Manages date, time, and currency format preferences
"""
import customtkinter as ctk
import yaml
from tkinter import messagebox
from pathlib import Path
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedComboBox
from src.core.theme_manager import theme_manager
from src.core.path_manager import path_manager
from src.core import config
from datetime import datetime

class LocaleSettingsSection:
    """Locale and format settings section"""
    
    # Date format options
    DATE_FORMATS = {
        "DD-MM-YYYY (20-01-2026)": "%d-%m-%Y",
        "MM-DD-YYYY (01-20-2026)": "%m-%d-%Y",
        "YYYY-MM-DD (2026-01-20)": "%Y-%m-%d",
        "DD/MM/YYYY (20/01/2026)": "%d/%m/%Y",
        "MM/DD/YYYY (01/20/2026)": "%m/%d/%Y",
        "DD.MM.YYYY (20.01.2026)": "%d.%m.%Y",
        "DD MMM YYYY (20 Jan 2026)": "%d %b %Y",
        "MMM DD, YYYY (Jan 20, 2026)": "%b %d, %Y",
    }
    
    # Time mode options
    TIME_MODES = {
        "12-hour (12:30 PM)": "12hr",
        "24-hour (14:30)": "24hr",
    }
    
    # Currency options
    CURRENCIES = {
        "Indian Rupee (₹)": {"symbol": "₹", "code": "INR"},
        "US Dollar ($)": {"symbol": "$", "code": "USD"},
        "Euro (€)": {"symbol": "€", "code": "EUR"},
        "British Pound (£)": {"symbol": "£", "code": "GBP"},
        "Japanese Yen (¥)": {"symbol": "¥", "code": "JPY"},
        "Russian Ruble (₽)": {"symbol": "₽", "code": "RUB"},
        "South Korean Won (₩)": {"symbol": "₩", "code": "KRW"},
        "Philippine Peso (₱)": {"symbol": "₱", "code": "PHP"},
    }
    
    # Currency position options
    CURRENCY_POSITIONS = {
        "Before amount (₹100)": "prefix",
        "After amount (100₹)": "suffix",
    }
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.section_frame = None
        self.config_path = path_manager.get_config_path()
    
    def create_section(self):
        """Create the locale settings section UI"""
        self.section_frame = ThemedFrame(self.parent, color_key="bg_secondary", corner_radius=10)
        self.section_frame.pack(fill="x", pady=(0, 20))
        self.section_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ThemedLabel(
            self.section_frame,
            text="Locale & Format Settings",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        ThemedLabel(
            self.section_frame,
            text="Customize date, time, and currency formats",
            color_key="fg_secondary"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Load current settings
        current_settings = self._load_current_settings()
        
        # Date Format
        self._create_setting_row(
            row=2,
            label="Date Format:",
            options=list(self.DATE_FORMATS.keys()),
            current_value=self._get_date_format_display(current_settings['date_format']),
            callback=self._on_date_format_change
        )
        
        # Time Mode
        self._create_setting_row(
            row=3,
            label="Time Format:",
            options=list(self.TIME_MODES.keys()),
            current_value=self._get_time_mode_display(current_settings['time_mode']),
            callback=self._on_time_mode_change
        )
        
        # Currency
        self._create_setting_row(
            row=4,
            label="Currency:",
            options=list(self.CURRENCIES.keys()),
            current_value=self._get_currency_display(current_settings['currency_symbol']),
            callback=self._on_currency_change
        )
        
        # Currency Position
        self._create_setting_row(
            row=5,
            label="Currency Position:",
            options=list(self.CURRENCY_POSITIONS.keys()),
            current_value=self._get_currency_position_display(current_settings['currency_position']),
            callback=self._on_currency_position_change
        )
        
        # Preview section
        self._create_preview_section(row=6, current_settings=current_settings)
        
        # Buttons
        btn_frame = ThemedFrame(self.section_frame, color_key="bg_secondary")
        btn_frame.grid(row=7, column=0, sticky="w", padx=20, pady=(15, 20))
        
        ThemedButton(
            btn_frame,
            text="Reset to Defaults",
            button_style="warning",
            width=150,
            command=self._reset_to_defaults
        ).pack(side="left", padx=(0, 10))
        
        ThemedButton(
            btn_frame,
            text="Apply Changes",
            button_style="accent",
            width=150,
            command=self._apply_changes
        ).pack(side="left")
        
        return self.section_frame
    
    def _create_setting_row(self, row, label, options, current_value, callback):
        """Create a setting row with label and dropdown"""
        container = ThemedFrame(self.section_frame, color_key="bg_secondary")
        container.grid(row=row, column=0, sticky="ew", padx=20, pady=5)
        container.grid_columnconfigure(1, weight=1)
        
        ThemedLabel(
            container,
            text=label,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        ).grid(row=0, column=0, sticky="w", padx=(0, 15))
        
        combo = ThemedComboBox(container, values=options, width=300)
        combo.set(current_value)
        combo.configure(command=callback)
        combo.grid(row=0, column=1, sticky="w")
        
        # Store reference
        if not hasattr(self, 'combos'):
            self.combos = {}
        self.combos[label] = combo
    
    def _create_preview_section(self, row, current_settings):
        """Create preview section showing current formats"""
        preview_frame = ThemedFrame(self.section_frame, color_key="bg_tertiary", corner_radius=6)
        preview_frame.grid(row=row, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        ThemedLabel(
            preview_frame,
            text="Preview",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Generate preview
        now = datetime.now()
        date_preview = now.strftime(current_settings['date_format'])
        time_preview = now.strftime(current_settings['time_format'])
        datetime_preview = now.strftime(current_settings['datetime_format'])
        currency_preview = self._format_currency(1234.56, current_settings)
        
        preview_text = f"Date: {date_preview}\n"
        preview_text += f"Time: {time_preview}\n"
        preview_text += f"DateTime: {datetime_preview}\n"
        preview_text += f"Currency: {currency_preview}"
        
        self.preview_label = ThemedLabel(
            preview_frame,
            text=preview_text,
            color_key="fg_secondary",
            justify="left"
        )
        self.preview_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def _load_current_settings(self):
        """Load current settings from config file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            datetime_config = config_data.get('datetime', {})
            currency_config = config_data.get('currency', {})
            
            return {
                'date_format': datetime_config.get('date_format', '%d-%m-%Y'),
                'time_format': datetime_config.get('time_format', '%I:%M %p'),
                'datetime_format': datetime_config.get('datetime_format', '%d-%m-%Y %I:%M %p'),
                'time_mode': datetime_config.get('time_mode', '12hr'),
                'currency_symbol': currency_config.get('symbol', '₹'),
                'currency_code': currency_config.get('code', 'INR'),
                'currency_position': currency_config.get('position', 'prefix'),
                'currency_decimal_places': currency_config.get('decimal_places', 2),
            }
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self._get_default_settings()
    
    def _get_default_settings(self):
        """Get default settings"""
        return {
            'date_format': '%d-%m-%Y',
            'time_format': '%I:%M %p',
            'datetime_format': '%d-%m-%Y %I:%M %p',
            'time_mode': '12hr',
            'currency_symbol': '₹',
            'currency_code': 'INR',
            'currency_position': 'prefix',
            'currency_decimal_places': 2,
        }
    
    def _get_date_format_display(self, format_code):
        """Get display name for date format code"""
        for display, code in self.DATE_FORMATS.items():
            if code == format_code:
                return display
        return list(self.DATE_FORMATS.keys())[0]
    
    def _get_time_mode_display(self, time_mode):
        """Get display name for time mode"""
        for display, mode in self.TIME_MODES.items():
            if mode == time_mode:
                return display
        return list(self.TIME_MODES.keys())[0]
    
    def _get_currency_display(self, symbol):
        """Get display name for currency symbol"""
        for display, curr in self.CURRENCIES.items():
            if curr['symbol'] == symbol:
                return display
        return list(self.CURRENCIES.keys())[0]
    
    def _get_currency_position_display(self, position):
        """Get display name for currency position"""
        for display, pos in self.CURRENCY_POSITIONS.items():
            if pos == position:
                return display
        return list(self.CURRENCY_POSITIONS.keys())[0]
    
    def _format_currency(self, amount, settings):
        """Format currency preview"""
        formatted = f"{amount:.{settings['currency_decimal_places']}f}"
        if settings['currency_position'] == 'prefix':
            return f"{settings['currency_symbol']}{formatted}"
        else:
            return f"{formatted}{settings['currency_symbol']}"
    
    def _on_date_format_change(self, value):
        """Handle date format change"""
        self._update_preview()
    
    def _on_time_mode_change(self, value):
        """Handle time mode change"""
        self._update_preview()
    
    def _on_currency_change(self, value):
        """Handle currency change"""
        self._update_preview()
    
    def _on_currency_position_change(self, value):
        """Handle currency position change"""
        self._update_preview()
    
    def _update_preview(self):
        """Update preview with current selections"""
        if not hasattr(self, 'preview_label'):
            return
        
        # Get current selections
        date_format_display = self.combos["Date Format:"].get()
        time_mode_display = self.combos["Time Format:"].get()
        currency_display = self.combos["Currency:"].get()
        currency_position_display = self.combos["Currency Position:"].get()
        
        # Convert to codes
        date_format = self.DATE_FORMATS[date_format_display]
        time_mode = self.TIME_MODES[time_mode_display]
        currency = self.CURRENCIES[currency_display]
        currency_position = self.CURRENCY_POSITIONS[currency_position_display]
        
        # Generate time format based on mode
        if time_mode == '12hr':
            time_format = '%I:%M %p'
            datetime_format = f"{date_format} %I:%M %p"
        else:
            time_format = '%H:%M'
            datetime_format = f"{date_format} %H:%M"
        
        # Generate preview
        now = datetime.now()
        date_preview = now.strftime(date_format)
        time_preview = now.strftime(time_format)
        datetime_preview = now.strftime(datetime_format)
        
        settings = {
            'currency_symbol': currency['symbol'],
            'currency_position': currency_position,
            'currency_decimal_places': 2
        }
        currency_preview = self._format_currency(1234.56, settings)
        
        preview_text = f"Date: {date_preview}\n"
        preview_text += f"Time: {time_preview}\n"
        preview_text += f"DateTime: {datetime_preview}\n"
        preview_text += f"Currency: {currency_preview}"
        
        self.preview_label.configure(text=preview_text)
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno(
            "Confirm Reset",
            "Reset all locale settings to defaults?\n\n"
            "This will restore:\n"
            "• Date format: DD-MM-YYYY\n"
            "• Time format: 12-hour\n"
            "• Currency: Indian Rupee (₹)\n\n"
            "Application restart required."
        ):
            try:
                # Load config
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                # Update with defaults
                defaults = self._get_default_settings()
                
                config_data['datetime'] = {
                    'date_format': defaults['date_format'],
                    'time_format': defaults['time_format'],
                    'datetime_format': defaults['datetime_format'],
                    'display_date_format': '%d %B %Y',
                    'display_datetime_format': '%d %B %Y %I:%M %p',
                    'time_mode': defaults['time_mode'],
                }
                
                config_data['currency'] = {
                    'symbol': defaults['currency_symbol'],
                    'code': defaults['currency_code'],
                    'position': defaults['currency_position'],
                    'decimal_places': defaults['currency_decimal_places'],
                }
                
                # Save config
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                messagebox.showinfo(
                    "Success",
                    "Locale settings reset to defaults.\n\nPlease restart the application."
                )
                
                # Refresh UI
                self._refresh_section()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _apply_changes(self):
        """Apply current settings to config file"""
        try:
            # Get current selections
            date_format_display = self.combos["Date Format:"].get()
            time_mode_display = self.combos["Time Format:"].get()
            currency_display = self.combos["Currency:"].get()
            currency_position_display = self.combos["Currency Position:"].get()
            
            # Convert to codes
            date_format = self.DATE_FORMATS[date_format_display]
            time_mode = self.TIME_MODES[time_mode_display]
            currency = self.CURRENCIES[currency_display]
            currency_position = self.CURRENCY_POSITIONS[currency_position_display]
            
            # Generate time format based on mode
            if time_mode == '12hr':
                time_format = '%I:%M %p'
                datetime_format = f"{date_format} %I:%M %p"
                display_datetime_format = f"%d %B %Y %I:%M %p"
            else:
                time_format = '%H:%M'
                datetime_format = f"{date_format} %H:%M"
                display_datetime_format = f"%d %B %Y %H:%M"
            
            # Load config
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Update settings
            config_data['datetime'] = {
                'date_format': date_format,
                'time_format': time_format,
                'datetime_format': datetime_format,
                'display_date_format': date_format.replace('%Y', '%Y').replace('%y', '%Y'),  # Keep year format
                'display_datetime_format': display_datetime_format,
                'time_mode': time_mode,
            }
            
            config_data['currency'] = {
                'symbol': currency['symbol'],
                'code': currency['code'],
                'position': currency_position,
                'decimal_places': 2,
            }
            
            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            messagebox.showinfo(
                "Success",
                "Locale settings updated successfully!\n\nPlease restart the application for changes to take effect."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _refresh_section(self):
        """Refresh the section to show updated settings"""
        if self.section_frame:
            self.section_frame.destroy()
        self.create_section()
