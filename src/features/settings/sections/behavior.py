"""
Behavior Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
import os
from pathlib import Path

from src.core.config import config


class BehaviorSection(QWidget):
    """Behavior settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup behavior settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Startup section
        startup_label = QLabel("Startup Behavior")
        startup_label.setProperty("class", "section-label")
        layout.addWidget(startup_label)
        
        # Start on Windows startup
        startup_layout = QHBoxLayout()
        self.startup_check = QCheckBox("Start Lifeboat when Windows starts")
        self.startup_check.setChecked(config.get('behavior.start_on_startup', False))
        self.startup_check.stateChanged.connect(self.on_value_changed)
        startup_layout.addWidget(self.startup_check)
        startup_layout.addStretch()
        layout.addLayout(startup_layout)
        
        startup_info = QLabel("App will automatically start when you log into Windows.")
        startup_info.setProperty("class", "secondary-text")
        startup_info.setWordWrap(True)
        layout.addWidget(startup_info)
        
        # Start minimized
        minimized_layout = QHBoxLayout()
        self.start_minimized_check = QCheckBox("Start minimized to system tray")
        self.start_minimized_check.setChecked(config.get('behavior.start_minimized', False))
        self.start_minimized_check.stateChanged.connect(self.on_value_changed)
        minimized_layout.addWidget(self.start_minimized_check)
        minimized_layout.addStretch()
        layout.addLayout(minimized_layout)
        
        minimized_info = QLabel("App will start in the background without showing the main window.")
        minimized_info.setProperty("class", "secondary-text")
        minimized_info.setWordWrap(True)
        layout.addWidget(minimized_info)
        
        # Separator
        layout.addSpacing(10)
        
        # System Tray section
        tray_label = QLabel("System Tray Behavior")
        tray_label.setProperty("class", "section-label")
        layout.addWidget(tray_label)
        
        # Minimize to tray
        min_tray_layout = QHBoxLayout()
        self.minimize_tray_check = QCheckBox("Minimize to system tray")
        self.minimize_tray_check.setChecked(config.get('behavior.minimize_to_tray', False))
        self.minimize_tray_check.stateChanged.connect(self.on_value_changed)
        min_tray_layout.addWidget(self.minimize_tray_check)
        min_tray_layout.addStretch()
        layout.addLayout(min_tray_layout)
        
        min_tray_info = QLabel("Minimize button hides the app to system tray instead of taskbar.")
        min_tray_info.setProperty("class", "secondary-text")
        min_tray_info.setWordWrap(True)
        layout.addWidget(min_tray_info)
        
        # Close to tray
        close_tray_layout = QHBoxLayout()
        self.close_tray_check = QCheckBox("Close button minimizes to tray")
        self.close_tray_check.setChecked(config.get('behavior.close_to_tray', False))
        self.close_tray_check.stateChanged.connect(self.on_value_changed)
        close_tray_layout.addWidget(self.close_tray_check)
        close_tray_layout.addStretch()
        layout.addLayout(close_tray_layout)
        
        close_tray_info = QLabel("Close button hides the app to system tray instead of quitting. Use tray menu to quit.")
        close_tray_info.setProperty("class", "secondary-text")
        close_tray_info.setWordWrap(True)
        layout.addWidget(close_tray_info)
        
        layout.addStretch()
        
        # Apply and Cancel buttons
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel Changes")
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.cancel_btn.setEnabled(False)
        apply_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.on_apply)
        self.apply_btn.setEnabled(False)
        apply_layout.addWidget(self.apply_btn)
        
        layout.addLayout(apply_layout)
        
        self.setLayout(layout)
    
    def on_value_changed(self):
        """Handle any value change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_apply(self):
        """Apply behavior changes"""
        # Track changes for logging
        changes = []
        
        # Save startup setting
        old_startup = config.get('behavior.start_on_startup', False)
        new_startup = self.startup_check.isChecked()
        if old_startup != new_startup:
            changes.append(f"Start on startup: {'enabled' if new_startup else 'disabled'}")
            self.set_startup(new_startup)
        config.set('behavior.start_on_startup', new_startup)
        
        # Save start minimized
        old_minimized = config.get('behavior.start_minimized', False)
        new_minimized = self.start_minimized_check.isChecked()
        if old_minimized != new_minimized:
            changes.append(f"Start minimized: {'enabled' if new_minimized else 'disabled'}")
        config.set('behavior.start_minimized', new_minimized)
        
        # Save minimize to tray
        old_min_tray = config.get('behavior.minimize_to_tray', False)
        new_min_tray = self.minimize_tray_check.isChecked()
        if old_min_tray != new_min_tray:
            changes.append(f"Minimize to tray: {'enabled' if new_min_tray else 'disabled'}")
        config.set('behavior.minimize_to_tray', new_min_tray)
        
        # Save close to tray
        old_close_tray = config.get('behavior.close_to_tray', False)
        new_close_tray = self.close_tray_check.isChecked()
        if old_close_tray != new_close_tray:
            changes.append(f"Close to tray: {'enabled' if new_close_tray else 'disabled'}")
        config.set('behavior.close_to_tray', new_close_tray)
        
        if config.save(log_changes=False):
            # Log changes if any
            if changes:
                from src.core.activity_logger import activity_logger
                from src.core.activity_formatter import format_settings_log
                action, details = format_settings_log('behavior', changes)
                activity_logger.log("Settings", action, details)
            
            # Update tray icon visibility
            self.update_tray_icon()
            
            self.apply_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
            # Show success notification
            from src.shared.dialogs import show_information
            show_information(
                self,
                "Success",
                "Behavior settings applied successfully!"
            )
        else:
            from src.shared.dialogs import show_warning
            show_warning(
                self,
                "Error",
                "Failed to save behavior settings."
            )
    
    def on_cancel(self):
        """Cancel behavior changes and revert to saved values"""
        # Reload values from config
        self.startup_check.setChecked(config.get('behavior.start_on_startup', False))
        self.start_minimized_check.setChecked(config.get('behavior.start_minimized', False))
        self.minimize_tray_check.setChecked(config.get('behavior.minimize_to_tray', False))
        self.close_tray_check.setChecked(config.get('behavior.close_to_tray', False))
        
        # Disable buttons
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
    
    def set_startup(self, enable: bool):
        """Set or remove Windows startup registry entry"""
        try:
            if sys.platform != 'win32':
                return
            
            import winreg
            
            # Registry path for startup programs
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "Lifeboat"
            
            # Get executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running from source - use pythonw to avoid console
                exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent.parent.parent / "main.py"}"'
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )
            
            if enable:
                # Add to startup
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                print(f"[Behavior] Added to Windows startup: {exe_path}")
            else:
                # Remove from startup
                try:
                    winreg.DeleteValue(key, app_name)
                    print("[Behavior] Removed from Windows startup")
                except FileNotFoundError:
                    # Already not in startup
                    pass
            
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"[Behavior] Error setting startup: {e}")
            from src.shared.dialogs import show_warning
            show_warning(
                self,
                "Startup Error",
                f"Could not modify Windows startup settings:\n{e}"
            )
    
    def update_tray_icon(self):
        """Update system tray icon visibility"""
        try:
            # Get the main window from the widget hierarchy
            widget = self
            while widget is not None:
                if hasattr(widget, 'tray_manager'):
                    widget.tray_manager.update_tray_visibility()
                    break
                widget = widget.parent()
        except Exception as e:
            print(f"[Behavior] Error updating tray icon: {e}")
