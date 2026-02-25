"""
Theme Manager
Handles theme loading, switching, and OS theme detection
"""
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from src.core.config import config
from src.models.theme import Theme
from src.core.database import db


class ThemeManager(QObject):
    """Manages application themes"""
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self):
        super().__init__()
        self.current_theme = None
        self.os_theme_mode = False
        self.last_detected_os_theme = None
        
        # Timer to check for OS theme changes
        self.os_theme_timer = QTimer()
        self.os_theme_timer.timeout.connect(self.check_os_theme_change)
        self.os_theme_timer.setInterval(2000)  # Check every 2 seconds
    
    def load_theme(self, theme_name: str = None) -> bool:
        """
        Load and apply a theme
        
        Args:
            theme_name: Name of theme to load, or None to use config
        
        Returns:
            bool: True if theme loaded successfully
        """
        if theme_name is None:
            theme_name = config.get('appearance.theme', 'Dark')
        
        # Check for OS theme mode
        if theme_name == "System":
            self.os_theme_mode = True
            theme_name = self.detect_os_theme()
            self.last_detected_os_theme = theme_name
            # Start monitoring OS theme changes
            if not self.os_theme_timer.isActive():
                self.os_theme_timer.start()
        else:
            self.os_theme_mode = False
            # Stop monitoring if not in system mode
            if self.os_theme_timer.isActive():
                self.os_theme_timer.stop()
        
        # Generate stylesheet from database theme
        stylesheet = self.generate_stylesheet(theme_name)
        if stylesheet:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                self.theme_changed.emit(theme_name)
                print(f"Applied theme: {theme_name}")
                return True
        
        print(f"Failed to apply theme: {theme_name}")
        return False
    
    def generate_stylesheet(self, theme_name: str) -> str:
        """
        Generate modern stylesheet from theme in database
        
        Args:
            theme_name: Name of theme
        
        Returns:
            str: Generated stylesheet
        """
        try:
            db.connect(reuse_if_open=True)
            theme = Theme.get(Theme.name == theme_name)
            db.close()
            
            # Generate modern QSS stylesheet from theme colors
            font_family = config.get('appearance.font_family', 'Segoe UI')
            font_size = config.get('appearance.font_size', 13)
            
            stylesheet = f"""
/* {theme_name} Theme - Generated Stylesheet */

* {{
    font-family: "{font_family}", Arial, sans-serif;
    font-size: {font_size}pt;
}}

/* Main Window */
QMainWindow, QWidget {{
    background-color: {theme.bg_primary};
    color: {theme.fg_primary};
}}

/* Navigation Sidebar */
#navigation {{
    background-color: {theme.bg_secondary};
    border-right: 1px solid {theme.border};
}}

#app-title {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    font-size: 15pt;
    font-weight: bold;
    border-bottom: 1px solid {theme.border};
}}

#nav-button {{
    background-color: transparent;
    color: {theme.fg_primary};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding-left: 20px;
    font-size: 11pt;
}}

#nav-button:hover {{
    background-color: {theme.bg_tertiary};
}}

#nav-button[active="true"] {{
    background-color: {theme.bg_tertiary};
    border-left: 3px solid {theme.accent};
    color: {theme.accent};
    font-weight: bold;
}}

/* Buttons */
QPushButton {{
    background-color: {theme.accent};
    color: {theme.bg_primary};
    border: none;
    border-radius: 6px;
    padding: 0.6em 1.2em;  /* Use em units to scale with font size */
    font-weight: 500;
    min-height: 2.4em;  /* Scale with font size */
    min-width: 5em;  /* Minimum width scales with font */
}}

QPushButton:hover {{
    background-color: {theme.accent_hover};
    color: {theme.bg_primary};
}}

QPushButton:pressed {{
    background-color: {theme.accent};
    color: {theme.bg_primary};
    padding: 9px 15px 7px 17px;
}}

QPushButton:disabled {{
    background-color: {theme.bg_tertiary};
    color: {theme.fg_secondary};
}}

/* Checkable Buttons (for AM/PM toggle) */
QPushButton:checkable {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_secondary};
    border: 1px solid {theme.border};
}}

QPushButton:checked {{
    background-color: {theme.accent};
    color: {theme.bg_primary};
    border: 2px solid {theme.accent};
    font-weight: bold;
}}

QPushButton:checkable:hover {{
    border: 1px solid {theme.accent};
}}

/* Input Fields */
QLineEdit, QPlainTextEdit {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
}}

QTextEdit {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
}}

QLineEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {theme.accent};
    padding: 7px 11px;
}}

QTextEdit:focus {{
    border: 2px solid {theme.accent};
}}

QLineEdit:hover, QPlainTextEdit:hover {{
    border: 1px solid {theme.accent};
}}

QTextEdit:hover {{
    border: 2px solid {theme.accent};
}}

/* ComboBox */
QComboBox {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 32px;
}}

QComboBox:hover {{
    border: 1px solid {theme.accent};
}}

QComboBox:focus {{
    border: 2px solid {theme.accent};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
    background-color: transparent;
}}

QComboBox::down-arrow {{
    image: url(assets/icons/arrow-down.svg);
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
    outline: none;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 4px;
    min-height: 32px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {theme.bg_tertiary};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {theme.accent};
}}

/* SpinBox */
QSpinBox, QDoubleSpinBox {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 32px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {theme.accent};
}}

QSpinBox:hover, QDoubleSpinBox:hover {{
    border: 1px solid {theme.accent};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 5px;
    width: 16px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {theme.accent};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom-right-radius: 5px;
    width: 16px;
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {theme.accent};
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url(assets/icons/arrow-up.svg);
    width: 10px;
    height: 10px;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url(assets/icons/arrow-down.svg);
    width: 10px;
    height: 10px;
}}

/* CheckBox */
QCheckBox {{
    background-color: transparent;
    color: {theme.fg_primary};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {theme.border};
    border-radius: 4px;
    background-color: {theme.bg_secondary};
}}

QCheckBox::indicator:hover {{
    border: 2px solid {theme.accent};
}}

QCheckBox::indicator:checked {{
    background-color: {theme.accent};
    border-color: {theme.accent};
    image: url(assets/icons/check.svg);
}}

/* RadioButton */
QRadioButton {{
    background-color: transparent;
    color: {theme.fg_primary};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {theme.border};
    border-radius: 10px;
    background-color: {theme.bg_secondary};
}}

QRadioButton::indicator:hover {{
    border: 2px solid {theme.accent};
}}

QRadioButton::indicator:checked {{
    background-color: {theme.accent};
    border-color: {theme.accent};
}}

/* ScrollBar Vertical */
QScrollBar:vertical {{
    background-color: {theme.bg_primary};
    width: 14px;
    border: none;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme.border};
    border-radius: 7px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme.fg_secondary};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {theme.accent};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ScrollBar Horizontal */
QScrollBar:horizontal {{
    background-color: {theme.bg_primary};
    height: 14px;
    border: none;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme.border};
    border-radius: 7px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme.fg_secondary};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {theme.accent};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ScrollArea */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

/* DateEdit, TimeEdit, DateTimeEdit */
QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 32px;
}}

QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border: 2px solid {theme.accent};
}}

QDateEdit:hover, QTimeEdit:hover, QDateTimeEdit:hover {{
    border: 1px solid {theme.accent};
}}

/* DateEdit dropdown button with calendar icon */
QDateEdit::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: center right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    width: 20px;
}}

QDateEdit::drop-down:hover {{
    background-color: {theme.accent};
}}

QDateEdit::down-arrow {{
    image: url(assets/icons/calendar.svg);
    width: 12px;
    height: 12px;
}}

/* DateTimeEdit dropdown button */
QDateTimeEdit::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: center right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    width: 20px;
}}

QDateTimeEdit::drop-down:hover {{
    background-color: {theme.accent};
}}

QDateTimeEdit::down-arrow {{
    image: url(assets/icons/calendar.svg);
    width: 12px;
    height: 12px;
}}

/* TimeEdit - up/down buttons instead of dropdown (MUST come after QDateEdit/QDateTimeEdit) */
QTimeEdit::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 5px;
    width: 16px;
}}

QTimeEdit::up-button:hover {{
    background-color: {theme.accent};
}}

QTimeEdit::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom-right-radius: 5px;
    width: 16px;
}}

QTimeEdit::down-button:hover {{
    background-color: {theme.accent};
}}

QTimeEdit::up-arrow {{
    image: url(assets/icons/arrow-up.svg);
    width: 10px;
    height: 10px;
}}

QTimeEdit::down-arrow {{
    image: url(assets/icons/arrow-down.svg);
    width: 10px;
    height: 10px;
}}

/* Calendar Widget */
QCalendarWidget {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 8px;
}}

QCalendarWidget QToolButton {{
    background-color: transparent;
    color: {theme.fg_primary};
    border: none;
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {theme.bg_tertiary};
}}

QCalendarWidget QToolButton:pressed {{
    background-color: {theme.accent};
}}

QCalendarWidget QMenu {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
}}

QCalendarWidget QSpinBox {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 4px;
    padding: 4px;
}}

QCalendarWidget QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 3px;
    width: 16px;
}}

QCalendarWidget QSpinBox::up-button:hover {{
    background-color: {theme.accent};
}}

QCalendarWidget QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 1px solid {theme.border};
    border-bottom-right-radius: 3px;
    width: 16px;
}}

QCalendarWidget QSpinBox::down-button:hover {{
    background-color: {theme.accent};
}}

QCalendarWidget QSpinBox::up-arrow {{
    image: url(assets/icons/arrow-up.svg);
    width: 10px;
    height: 10px;
}}

QCalendarWidget QSpinBox::down-arrow {{
    image: url(assets/icons/arrow-down.svg);
    width: 10px;
    height: 10px;
}}

QCalendarWidget QToolButton::menu-indicator {{
    image: none;
    width: 0px;
    height: 0px;
}}

QCalendarWidget QAbstractItemView {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
    border: none;
}}

/* Dialog */
QDialog {{
    background-color: {theme.bg_primary};
    color: {theme.fg_primary};
}}

/* MessageBox */
QMessageBox {{
    background-color: {theme.bg_primary};
    color: {theme.fg_primary};
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 8px 16px;
}}

/* TabWidget */
QTabWidget::pane {{
    border: 1px solid {theme.border};
    background-color: {theme.bg_primary};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_secondary};
    border: 1px solid {theme.border};
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {theme.accent};
    color: {theme.fg_primary};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme.bg_tertiary};
}}

/* Menu */
QMenu {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {theme.accent};
}}

QMenu::separator {{
    height: 1px;
    background-color: {theme.border};
    margin: 4px 8px;
}}

/* ToolTip */
QToolTip {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 1px solid {theme.border};
    border-radius: 4px;
    padding: 6px 10px;
}}

/* Frames */
QFrame {{
    background-color: transparent;
    border: none;
}}

/* Labels */
QLabel {{
    background-color: transparent;
    color: {theme.fg_primary};
}}

/* Custom Components */
#settings-section {{
    background-color: {theme.bg_secondary};
    border: 1px solid {theme.border};
    border-radius: 8px;
    padding: 20px;
}}

#summary-card {{
    background-color: {theme.bg_secondary};
    border: 1px solid {theme.border};
    border-radius: 8px;
    padding: 20px;
}}

#task-item {{
    background-color: {theme.bg_secondary};
    border: 1px solid {theme.border};
    border-radius: 8px;
    padding: 15px;
}}

#task-item:hover {{
    border-color: {theme.accent};
}}

/* Expense/Income Items */
QFrame[class="expense-item"], QFrame[class="income-item"] {{
    background-color: {theme.bg_secondary};
    border: 1px solid {theme.border};
    border-radius: 8px;
    padding: 15px;
}}

QFrame[class="expense-item"]:hover, QFrame[class="income-item"]:hover {{
    border-color: {theme.accent};
}}

/* Warning/Info Boxes */
QFrame[class="warning-box"], QFrame[class="info-box"] {{
    background-color: {theme.bg_tertiary};
    border-radius: 6px;
    padding: 15px;
}}

/* Path/Settings Containers */
QFrame[class="path-container"], QFrame[class="theme-item"] {{
    background-color: {theme.bg_tertiary};
    border-radius: 8px;
    padding: 15px;
}}

/* Secondary Text */
QLabel[class="secondary-text"] {{
    color: {theme.fg_secondary};
}}

QLabel[class="small-text"] {{
    color: {theme.fg_secondary};
    font-size: 8pt;
}}

QLabel[class="meta-text"] {{
    color: {theme.fg_secondary};
    font-size: 9pt;
}}

QLabel[class="title-text"] {{
    color: {theme.fg_secondary};
    font-size: 11pt;
}}

/* Success/Warning/Danger Buttons */
QPushButton[class="danger-button"] {{
    background-color: {theme.danger};
}}

QPushButton[class="danger-button"]:hover {{
    background-color: {theme.danger};
    opacity: 0.9;
}}

QPushButton[class="warning-button"] {{
    background-color: {theme.warning};
}}

QPushButton[class="warning-button"]:hover {{
    background-color: {theme.warning};
    opacity: 0.9;
}}

QPushButton[class="success-button"] {{
    background-color: {theme.success};
}}

QPushButton[class="success-button"]:hover {{
    background-color: {theme.success};
    opacity: 0.9;
}}

/* Active/Status Labels */
QLabel[class="active-label"] {{
    color: {theme.success};
    font-weight: bold;
}}

QLabel[class="accent-label"] {{
    color: {theme.accent};
}}
"""
            return stylesheet
            
        except Exception as e:
            print(f"Error generating stylesheet: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def detect_os_theme(self) -> str:
        """
        Detect OS theme (dark or light)
        
        Returns:
            str: "Dark" or "Light"
        """
        try:
            # Try using darkdetect if available
            import darkdetect
            is_dark = darkdetect.isDark()
            return "Dark" if is_dark else "Light"
        except ImportError:
            # Fallback: Try Qt palette detection
            app = QApplication.instance()
            if app:
                palette = app.palette()
                bg_color = palette.window().color()
                # If background is dark (luminance < 128), use dark theme
                luminance = (0.299 * bg_color.red() + 
                           0.587 * bg_color.green() + 
                           0.114 * bg_color.blue())
                return "Dark" if luminance < 128 else "Light"
        
        # Default to Dark
        return "Dark"
    
    def check_os_theme_change(self):
        """Check if OS theme has changed and update if needed"""
        if self.os_theme_mode:
            current_os_theme = self.detect_os_theme()
            if current_os_theme != self.last_detected_os_theme:
                print(f"OS theme changed from {self.last_detected_os_theme} to {current_os_theme}")
                self.last_detected_os_theme = current_os_theme
                self.load_theme("System")
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set and save theme
        
        Args:
            theme_name: Name of theme to set
        
        Returns:
            bool: True if successful
        """
        # Update config
        config.set('appearance.theme', theme_name)
        config.save()
        
        # Load theme
        return self.load_theme(theme_name)
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        try:
            db.connect(reuse_if_open=True)
            themes = [theme.name for theme in Theme.select()]
            db.close()
            
            # Add System option
            return ["System"] + themes
        except Exception as e:
            print(f"Error getting themes: {e}")
            return ["System", "Dark", "Light"]
    
    def get_all_themes(self) -> list:
        """Get all theme objects from database"""
        try:
            db.connect(reuse_if_open=True)
            themes = list(Theme.select())
            db.close()
            return themes
        except Exception as e:
            print(f"Error getting themes: {e}")
            return []
    
    def get_theme_by_name(self, name: str):
        """Get theme object by name"""
        try:
            db.connect(reuse_if_open=True)
            theme = Theme.get(Theme.name == name)
            db.close()
            return theme
        except Exception as e:
            print(f"Error getting theme: {e}")
            return None
    
    def create_custom_theme(self, colors: dict, base_name: str = None) -> bool:
        """
        Create a custom theme
        
        Args:
            colors: Dictionary of color values
            base_name: Base theme name (for naming custom theme)
        
        Returns:
            bool: True if successful
        """
        try:
            db.connect(reuse_if_open=True)
            
            # Generate custom theme name
            if base_name:
                custom_name = f"Custom {base_name}"
            else:
                custom_name = "Custom Theme"
            
            # Check if name exists, add number if needed
            counter = 1
            original_name = custom_name
            while Theme.select().where(Theme.name == custom_name).exists():
                custom_name = f"{original_name} {counter}"
                counter += 1
            
            # Create theme with all required fields
            Theme.create(
                name=custom_name,
                is_custom=True,
                is_active=False,
                bg_primary=colors.get('bg_primary', '#1a1a1a'),
                bg_secondary=colors.get('bg_secondary', '#2d2d2d'),
                bg_tertiary=colors.get('bg_tertiary', '#3d3d3d'),
                fg_primary=colors.get('fg_primary', '#ffffff'),
                fg_secondary=colors.get('fg_secondary', '#b0b0b0'),
                accent=colors.get('accent', '#0078d4'),
                accent_hover=colors.get('accent_hover', '#106ebe'),
                success=colors.get('success', '#28a745'),
                warning=colors.get('warning', '#ffc107'),
                danger=colors.get('danger', '#dc3545'),
                border=colors.get('border', '#4d4d4d')
            )
            
            db.close()
            print(f"Created custom theme: {custom_name}")
            return True
        except Exception as e:
            print(f"Error creating custom theme: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_theme(self, theme_name: str, colors: dict) -> bool:
        """
        Update an existing theme
        
        Args:
            theme_name: Name of theme to update
            colors: Dictionary of color values
        
        Returns:
            bool: True if successful
        """
        try:
            db.connect(reuse_if_open=True)
            
            theme = Theme.get(Theme.name == theme_name)
            
            # Update all color fields
            theme.bg_primary = colors.get('bg_primary', theme.bg_primary)
            theme.bg_secondary = colors.get('bg_secondary', theme.bg_secondary)
            theme.bg_tertiary = colors.get('bg_tertiary', theme.bg_tertiary)
            theme.fg_primary = colors.get('fg_primary', theme.fg_primary)
            theme.fg_secondary = colors.get('fg_secondary', theme.fg_secondary)
            theme.accent = colors.get('accent', theme.accent)
            theme.accent_hover = colors.get('accent_hover', theme.accent_hover)
            theme.success = colors.get('success', theme.success)
            theme.warning = colors.get('warning', theme.warning)
            theme.danger = colors.get('danger', theme.danger)
            theme.border = colors.get('border', theme.border)
            
            theme.save()
            
            db.close()
            print(f"Updated theme: {theme_name}")
            return True
        except Exception as e:
            print(f"Error updating theme: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """
        Delete a custom theme
        
        Args:
            theme_name: Name of theme to delete
        
        Returns:
            bool: True if successful
        """
        try:
            db.connect(reuse_if_open=True)
            
            theme = Theme.get(Theme.name == theme_name)
            if theme.is_custom:
                theme.delete_instance()
                db.close()
                return True
            
            db.close()
            return False
        except Exception as e:
            print(f"Error deleting theme: {e}")
            return False
    
    def get_active_theme(self) -> str:
        """Get currently active theme name"""
        if self.os_theme_mode:
            return "System"
        return self.current_theme or "Dark"


# Global theme manager instance
theme_manager = ThemeManager()
