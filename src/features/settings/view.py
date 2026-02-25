"""
Settings View
Main settings page with change tracking
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.features.settings.sections.appearance import AppearanceSection
from src.features.settings.sections.locale import LocaleSection
from src.features.settings.sections.themes import ThemesSection
from src.features.settings.sections.paths import PathsSection
from src.features.settings.sections.about import AboutSection
from src.features.settings.change_tracker import change_tracker


class SettingsView(QWidget):
    """Settings main view with change tracking"""
    
    # Signal to request navigation away
    navigation_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        from PyQt6.QtGui import QFont
        header = QLabel("⚙ Settings")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        main_layout.addWidget(header)
        
        # Scroll area for settings sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add settings sections
        self.appearance_section = AppearanceSection()
        self.themes_section = ThemesSection()
        self.locale_section = LocaleSection()
        self.paths_section = PathsSection()
        self.about_section = AboutSection()
        
        content_layout.addWidget(self.create_section("Appearance", self.appearance_section))
        content_layout.addWidget(self.create_section("Themes", self.themes_section))
        content_layout.addWidget(self.create_section("Locale & Format", self.locale_section))
        content_layout.addWidget(self.create_section("File Locations", self.paths_section))
        content_layout.addWidget(self.create_section("About", self.about_section))
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_section(self, title: str, section_widget: QWidget) -> QFrame:
        """Create a settings section container"""
        container = QFrame()
        container.setObjectName("settings-section")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        
        # Section title
        from PyQt6.QtGui import QFont
        title_label = QLabel(title)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Section content
        layout.addWidget(section_widget)
        
        container.setLayout(layout)
        return container
    
    def check_unsaved_changes(self) -> bool:
        """
        Check for unsaved changes and prompt user
        Returns True if navigation should proceed, False if cancelled
        """
        if not change_tracker.has_changes():
            return True
        
        # Build message with changes
        changes_list = change_tracker.get_changes_summary()
        changes_text = "\n".join(f"• {change}" for change in changes_list)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("You have unsaved changes in Settings:")
        msg.setInformativeText(changes_text)
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Add custom buttons
        apply_btn = msg.addButton("Apply Changes", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton("Discard Changes", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        clicked = msg.clickedButton()
        
        if clicked == apply_btn:
            # Apply changes
            self.apply_all_changes()
            return True
        elif clicked == discard_btn:
            # Discard changes
            change_tracker.clear()
            return True
        else:
            # Cancel navigation
            return False
    
    def apply_all_changes(self):
        """Apply all pending changes"""
        if not change_tracker.has_changes():
            return
        
        # Check if restart is needed
        needs_restart = change_tracker.needs_restart()
        
        # Clear tracker
        change_tracker.clear()
        
        # Show restart prompt if needed
        if needs_restart:
            self.show_restart_prompt()
    
    def show_restart_prompt(self):
        """Show prompt to restart application"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Restart Required")
        msg.setText("Some changes require restarting the application to take effect.")
        msg.setInformativeText("Would you like to restart now?")
        msg.setIcon(QMessageBox.Icon.Information)
        
        restart_now = msg.addButton("Restart Now", QMessageBox.ButtonRole.AcceptRole)
        restart_later = msg.addButton("Restart Later", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == restart_now:
            self.restart_application()
    
    def restart_application(self):
        """Restart the application"""
        import sys
        import os
        import subprocess
        from PyQt6.QtWidgets import QApplication
        
        # Close the current application
        QApplication.instance().quit()
        
        # Check if running as packaged app or script
        if getattr(sys, 'frozen', False):
            # Running as packaged executable
            executable = sys.executable
            if os.name == 'nt':  # Windows
                # Use CREATE_NO_WINDOW to prevent console window
                subprocess.Popen([executable], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([executable])
        else:
            # Running as script
            python = sys.executable
            script = sys.argv[0]
            if os.name == 'nt':  # Windows
                # Use pythonw.exe if available to avoid console window
                pythonw = python.replace('python.exe', 'pythonw.exe')
                if os.path.exists(pythonw):
                    subprocess.Popen([pythonw, script])
                else:
                    subprocess.Popen([python, script], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([python, script])
    
    def refresh(self):
        """Refresh view to apply config changes"""
        pass

