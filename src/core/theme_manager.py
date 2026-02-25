"""
Theme Manager
Handles theme loading, switching, and OS theme detection
"""
import sys
import yaml
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from src.core.config import config
from src.core.path_manager import path_manager
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
    
    def _load_themes_yaml(self):
        """Load custom themes from themes.yaml"""
        try:
            themes_path = path_manager.get_themes_path()
            if not themes_path.exists():
                return []
            
            with open(themes_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('custom_themes', []) if data else []
        except Exception as e:
            print(f"Error loading themes.yaml: {e}")
            return []
    
    def _save_themes_yaml(self, themes_list):
        """Save custom themes to themes.yaml"""
        try:
            themes_path = path_manager.get_themes_path()
            with open(themes_path, 'w', encoding='utf-8') as f:
                yaml.dump({'custom_themes': themes_list}, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving themes.yaml: {e}")
            return False
    
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
        Generate modern stylesheet from theme (checks themes.yaml first, then database)
        
        Args:
            theme_name: Name of theme
        
        Returns:
            str: Generated stylesheet
        """
        try:
            # First check themes.yaml for custom themes
            yaml_themes = self._load_themes_yaml()
            theme_data = next((t for t in yaml_themes if t.get('name') == theme_name), None)
            
            if theme_data:
                # Use theme from YAML - create a simple object
                class ThemeObj:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                theme = ThemeObj(theme_data)
            else:
                # Fall back to database
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
}}

#app-title {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_secondary},
        stop:1 {theme.bg_tertiary});
    color: {theme.fg_primary};
    font-size: 15pt;
    font-weight: bold;
    border-bottom: 2px solid {theme.border};
}}

#nav-button {{
    background-color: transparent;
    color: {theme.fg_primary};
    border: none;
    border-left: 3px solid transparent;
    border-right: 2px solid transparent;
    text-align: left;
    padding-left: 20px;
    font-size: 11pt;
    margin: 2px 0px;
}}

#nav-button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {theme.bg_tertiary},
        stop:1 transparent);
    border-right: 2px solid {theme.accent};
}}

#nav-button[active="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {theme.bg_tertiary},
        stop:1 transparent);
    border-left: 3px solid {theme.accent};
    border-right: 2px solid {theme.accent};
    color: {theme.accent};
    font-weight: bold;
}}

/* Buttons */
QPushButton {{
    background-color: {theme.accent};
    color: {theme.bg_primary};
    border: 2px solid {theme.accent};
    border-radius: 8px;
    padding: 0.6em 1.2em;  /* Use em units to scale with font size */
    font-weight: 500;
    min-height: 2.4em;  /* Scale with font size */
    min-width: 5em;  /* Minimum width scales with font */
}}

QPushButton:hover {{
    background-color: {theme.accent_hover};
    border-color: {theme.accent_hover};
    color: {theme.bg_primary};
}}

QPushButton:pressed {{
    background-color: {theme.accent};
    border-color: {theme.accent};
    color: {theme.bg_primary};
    padding: 9px 15px 7px 17px;
}}

QPushButton:disabled {{
    background-color: {theme.bg_tertiary};
    color: {theme.fg_secondary};
    border-color: {theme.border};
}}

/* Checkable Buttons (for AM/PM toggle) */
QPushButton:checkable {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_secondary};
    border: 2px solid {theme.border};
}}

QPushButton:checked {{
    background-color: {theme.accent};
    color: {theme.bg_primary};
    border: 2px solid {theme.accent};
    font-weight: bold;
}}

QPushButton:checkable:hover {{
    border: 2px solid {theme.accent};
}}

/* Input Fields */
QLineEdit, QPlainTextEdit {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
}}

QTextEdit {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 8px;
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
    border: 2px solid {theme.border};
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 32px;
}}

QComboBox:hover {{
    border: 2px solid {theme.accent};
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
    border: 2px solid {theme.accent};
    border-radius: 8px;
    selection-background-color: {theme.accent};
    selection-color: {theme.fg_primary};
    outline: none;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 6px;
    min-height: 32px;
    border: 1px solid transparent;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {theme.bg_tertiary};
    border: 1px solid {theme.accent};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {theme.accent};
    border: 1px solid {theme.accent};
}}

/* SpinBox */
QSpinBox, QDoubleSpinBox {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 32px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {theme.accent};
}}

QSpinBox:hover, QDoubleSpinBox:hover {{
    border: 2px solid {theme.accent};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 6px;
    width: 16px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {theme.accent};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-bottom-right-radius: 6px;
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
    border-radius: 5px;
    background-color: {theme.bg_secondary};
}}

QCheckBox::indicator:hover {{
    border: 2px solid {theme.accent};
    background-color: {theme.bg_tertiary};
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
    background-color: {theme.bg_tertiary};
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
    border: 1px solid {theme.border};
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme.fg_secondary};
    border-color: {theme.accent};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {theme.accent};
    border-color: {theme.accent};
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
    border: 1px solid {theme.border};
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme.fg_secondary};
    border-color: {theme.accent};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {theme.accent};
    border-color: {theme.accent};
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
    border: 2px solid {theme.border};
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 32px;
}}

QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border: 2px solid {theme.accent};
}}

QDateEdit:hover, QTimeEdit:hover, QDateTimeEdit:hover {{
    border: 2px solid {theme.accent};
}}

/* DateEdit dropdown button with calendar icon */
QDateEdit::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: center right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
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
    border-left: 2px solid {theme.border};
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
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
    border-left: 2px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 6px;
    width: 16px;
}}

QTimeEdit::up-button:hover {{
    background-color: {theme.accent};
}}

QTimeEdit::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-bottom-right-radius: 6px;
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
    border: 2px solid {theme.border};
    border-radius: 10px;
}}

QCalendarWidget QToolButton {{
    background-color: transparent;
    color: {theme.fg_primary};
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px;
    margin: 2px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {theme.bg_tertiary};
    border: 1px solid {theme.accent};
}}

QCalendarWidget QToolButton:pressed {{
    background-color: {theme.accent};
    border: 1px solid {theme.accent};
}}

QCalendarWidget QMenu {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
}}

QCalendarWidget QSpinBox {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 6px;
    padding: 4px;
}}

QCalendarWidget QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-bottom: 1px solid {theme.border};
    border-top-right-radius: 4px;
    width: 16px;
}}

QCalendarWidget QSpinBox::up-button:hover {{
    background-color: {theme.accent};
}}

QCalendarWidget QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    background-color: {theme.bg_tertiary};
    border-left: 2px solid {theme.border};
    border-bottom-right-radius: 4px;
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
    border: 2px solid {theme.border};
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
    border: 2px solid {theme.border};
    background-color: {theme.bg_primary};
    border-radius: 10px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_secondary};
    border: 2px solid {theme.border};
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTabBar::tab:selected {{
    background-color: {theme.accent};
    color: {theme.fg_primary};
    border-color: {theme.accent};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme.bg_tertiary};
    border-color: {theme.accent};
}}

/* Menu */
QMenu {{
    background-color: {theme.bg_secondary};
    color: {theme.fg_primary};
    border: 2px solid {theme.border};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 6px;
    border: 1px solid transparent;
}}

QMenu::item:selected {{
    background-color: {theme.accent};
    border: 1px solid {theme.accent};
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
    border: 2px solid {theme.accent};
    border-radius: 6px;
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
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_secondary},
        stop:1 {theme.bg_tertiary});
    border: 2px solid {theme.border};
    border-radius: 10px;
    padding: 20px;
}}

#summary-card {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_secondary},
        stop:1 {theme.bg_tertiary});
    border: 2px solid {theme.border};
    border-radius: 10px;
    padding: 20px;
}}

#task-item {{
    background-color: {theme.bg_secondary};
    border: 2px solid {theme.border};
    border-radius: 10px;
    padding: 15px;
}}

#task-item:hover {{
    border-color: {theme.accent};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_secondary},
        stop:1 {theme.bg_tertiary});
}}

/* Expense/Income Items */
QFrame[class="expense-item"], QFrame[class="income-item"] {{
    background-color: {theme.bg_secondary};
    border: 2px solid {theme.border};
    border-radius: 10px;
    padding: 15px;
}}

QFrame[class="expense-item"]:hover, QFrame[class="income-item"]:hover {{
    border-color: {theme.accent};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_secondary},
        stop:1 {theme.bg_tertiary});
}}

/* Warning/Info Boxes */
QFrame[class="warning-box"] {{
    background-color: {theme.bg_tertiary};
    border: 2px solid {theme.warning};
    border-radius: 8px;
    padding: 15px;
}}

QFrame[class="info-box"] {{
    background-color: {theme.bg_tertiary};
    border: 2px solid {theme.accent};
    border-radius: 8px;
    padding: 15px;
}}

/* Path/Settings Containers */
QFrame[class="path-container"], QFrame[class="theme-item"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {theme.bg_tertiary},
        stop:1 {theme.bg_secondary});
    border: 2px solid {theme.border};
    border-radius: 10px;
    padding: 15px;
}}

QFrame[class="path-container"]:hover, QFrame[class="theme-item"]:hover {{
    border-color: {theme.accent};
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
        """Get all theme objects from database and themes.yaml"""
        try:
            # Get built-in themes from database
            db.connect(reuse_if_open=True)
            db_themes = list(Theme.select().where(Theme.is_custom == False))
            db.close()
            
            # Get custom themes from YAML
            yaml_themes_data = self._load_themes_yaml()
            
            # Convert YAML themes to Theme-like objects
            yaml_themes = []
            for theme_data in yaml_themes_data:
                theme_obj = type('Theme', (), {
                    'name': theme_data.get('name', 'Unnamed'),
                    'is_custom': True,
                    **theme_data
                })()
                yaml_themes.append(theme_obj)
            
            return db_themes + yaml_themes
        except Exception as e:
            print(f"Error getting themes: {e}")
            return []
    
    def get_theme_by_name(self, name: str):
        """Get theme object by name (checks themes.yaml first, then database)"""
        try:
            # First check themes.yaml
            yaml_themes = self._load_themes_yaml()
            theme_data = next((t for t in yaml_themes if t.get('name') == name), None)
            
            if theme_data:
                # Return theme-like object from YAML
                return type('Theme', (), {
                    'name': theme_data.get('name', 'Unnamed'),
                    'is_custom': True,
                    **theme_data
                })()
            
            # Fall back to database
            db.connect(reuse_if_open=True)
            theme = Theme.get(Theme.name == name)
            db.close()
            return theme
        except Exception as e:
            print(f"Error getting theme: {e}")
            return None
    
    def create_custom_theme(self, colors: dict, base_name: str = None) -> bool:
        """
        Create a custom theme in themes.yaml
        
        Args:
            colors: Dictionary of color values (including 'name' key)
            base_name: Base theme name (for naming custom theme, deprecated)
        
        Returns:
            bool: True if successful
        """
        try:
            # Get custom name from colors dict, or generate one
            if 'name' in colors and colors['name']:
                custom_name = colors['name']
            elif base_name:
                custom_name = f"Custom {base_name}"
            else:
                custom_name = "Custom Theme"
            
            # Load existing themes
            themes_list = self._load_themes_yaml()
            
            # Check if name exists, add number if needed
            counter = 1
            original_name = custom_name
            existing_names = [t.get('name') for t in themes_list]
            while custom_name in existing_names:
                custom_name = f"{original_name} {counter}"
                counter += 1
            
            # Create theme dict
            new_theme = {
                'name': custom_name,
                'bg_primary': colors.get('bg_primary', '#1a1a1a'),
                'bg_secondary': colors.get('bg_secondary', '#2d2d2d'),
                'bg_tertiary': colors.get('bg_tertiary', '#3d3d3d'),
                'fg_primary': colors.get('fg_primary', '#ffffff'),
                'fg_secondary': colors.get('fg_secondary', '#b0b0b0'),
                'accent': colors.get('accent', '#0078d4'),
                'accent_hover': colors.get('accent_hover', '#106ebe'),
                'success': colors.get('success', '#28a745'),
                'warning': colors.get('warning', '#ffc107'),
                'danger': colors.get('danger', '#dc3545'),
                'border': colors.get('border', '#4d4d4d')
            }
            
            themes_list.append(new_theme)
            
            if self._save_themes_yaml(themes_list):
                print(f"Created custom theme: {custom_name}")
                return True
            return False
        except Exception as e:
            print(f"Error creating custom theme: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_theme(self, theme_name: str, colors: dict) -> bool:
        """
        Update an existing theme in themes.yaml
        
        Args:
            theme_name: Name of theme to update
            colors: Dictionary of color values (including optional 'name' key for renaming)
        
        Returns:
            bool: True if successful
        """
        try:
            themes_list = self._load_themes_yaml()
            
            # Find the theme
            theme_index = next((i for i, t in enumerate(themes_list) if t.get('name') == theme_name), None)
            
            if theme_index is None:
                print(f"Theme '{theme_name}' not found in themes.yaml")
                return False
            
            # Check if renaming
            new_name = colors.get('name', '').strip()
            if new_name and new_name != theme_name:
                # Check if new name already exists
                existing_names = [t.get('name') for i, t in enumerate(themes_list) if i != theme_index]
                if new_name in existing_names:
                    print(f"Theme name '{new_name}' already exists")
                    return False
                
                # Update active theme in config if this theme is active
                if config.get('appearance.theme') == theme_name:
                    config.set('appearance.theme', new_name)
                    config.save()
                
                themes_list[theme_index]['name'] = new_name
            
            # Update all color fields
            theme = themes_list[theme_index]
            theme['bg_primary'] = colors.get('bg_primary', theme.get('bg_primary'))
            theme['bg_secondary'] = colors.get('bg_secondary', theme.get('bg_secondary'))
            theme['bg_tertiary'] = colors.get('bg_tertiary', theme.get('bg_tertiary'))
            theme['fg_primary'] = colors.get('fg_primary', theme.get('fg_primary'))
            theme['fg_secondary'] = colors.get('fg_secondary', theme.get('fg_secondary'))
            theme['accent'] = colors.get('accent', theme.get('accent'))
            theme['accent_hover'] = colors.get('accent_hover', theme.get('accent_hover'))
            theme['success'] = colors.get('success', theme.get('success'))
            theme['warning'] = colors.get('warning', theme.get('warning'))
            theme['danger'] = colors.get('danger', theme.get('danger'))
            theme['border'] = colors.get('border', theme.get('border'))
            
            if self._save_themes_yaml(themes_list):
                print(f"Updated theme: {theme['name']}")
                return True
            return False
        except Exception as e:
            print(f"Error updating theme: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """
        Delete a custom theme from themes.yaml
        
        Args:
            theme_name: Name of theme to delete
        
        Returns:
            bool: True if successful
        """
        try:
            themes_list = self._load_themes_yaml()
            
            # Find and remove the theme
            original_length = len(themes_list)
            themes_list = [t for t in themes_list if t.get('name') != theme_name]
            
            if len(themes_list) == original_length:
                print(f"Theme '{theme_name}' not found in themes.yaml")
                return False
            
            # If deleting active theme, switch to Dark
            if config.get('appearance.theme') == theme_name:
                config.set('appearance.theme', 'Dark')
                config.save()
            
            if self._save_themes_yaml(themes_list):
                print(f"Deleted theme: {theme_name}")
                return True
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
