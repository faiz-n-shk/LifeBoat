"""
Paths Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from src.core.path_manager import path_manager


class PathsSection(QWidget):
    """File paths settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup paths settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Description
        desc = QLabel("Customize where your configuration and database files are stored")
        desc.setProperty("class", "secondary-text")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Get current paths info
        paths_info = path_manager.get_current_paths_info()
        
        # Config file section
        self.config_section = self.create_path_section(
            "Configuration File (config.yaml)",
            paths_info['config']['current'],
            paths_info['config']['is_custom'],
            self.on_browse_config,
            self.on_reset_config,
            self.on_restore_config
        )
        layout.addWidget(self.config_section)
        
        # Themes file section
        self.themes_section = self.create_path_section(
            "Themes File (themes.yaml)",
            paths_info['themes']['current'],
            paths_info['themes']['is_custom'],
            self.on_browse_themes,
            self.on_reset_themes,
            None
        )
        layout.addWidget(self.themes_section)
        
        # Database file section
        self.database_section = self.create_path_section(
            "Database File (lifeboat.db)",
            paths_info['database']['current'],
            paths_info['database']['is_custom'],
            self.on_browse_database,
            self.on_reset_database,
            self.on_restore_database
        )
        layout.addWidget(self.database_section)
        
        # Logs directory section
        self.logs_section = self.create_path_section(
            "Logs Directory",
            paths_info['logs']['current'],
            paths_info['logs']['is_custom'],
            self.on_browse_logs,
            self.on_reset_logs,
            None
        )
        layout.addWidget(self.logs_section)
        
        # Warning message
        warning = QFrame()
        warning.setProperty("class", "warning-box")
        warning_layout = QVBoxLayout(warning)
        
        warning_title = QLabel("⚠ Important")
        warning_title.setStyleSheet("font-weight: bold;")
        warning_layout.addWidget(warning_title)
        
        warning_text = QLabel(
            "• Changing file locations requires restarting the application\n"
            "• Original files remain in the app directory as backup\n"
            "• Use 'Restore Defaults' if files become corrupted\n"
            "• Always manually backup 'config.yaml' and 'lifeboat.db' for safety"
        )
        warning_text.setProperty("class", "meta-text")
        warning_layout.addWidget(warning_text)
        
        layout.addWidget(warning)
        
        self.setLayout(layout)
    
    def create_path_section(self, title, current_path, is_custom, on_browse, on_reset, on_restore):
        """Create a path configuration section"""
        container = QFrame()
        container.setProperty("class", "path-container")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Title
        from PyQt6.QtGui import QFont
        title_label = QLabel(title)
        font = QFont()
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Status and path
        status_text = "Custom Location" if is_custom else "Default Location"
        status_label = QLabel(status_text)
        status_label.setProperty("class", "accent-label" if is_custom else "secondary-text")
        layout.addWidget(status_label)
        
        path_label = QLabel(current_path)
        path_label.setProperty("class", "small-text")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(on_browse)
        btn_layout.addWidget(browse_btn)
        
        if is_custom:
            reset_btn = QPushButton("Reset to Default")
            reset_btn.clicked.connect(on_reset)
            btn_layout.addWidget(reset_btn)
        
        if on_restore:
            restore_btn = QPushButton("Restore Defaults")
            restore_btn.clicked.connect(on_restore)
            btn_layout.addWidget(restore_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        return container
    
    def on_browse_config(self):
        """Browse for custom config directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Config File"
        )
        
        if directory:
            success, message = path_manager.set_custom_config_path(directory)
            if success:
                # Log path change
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "changed config path", directory)
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Config Path Changed",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_browse_database(self):
        """Browse for custom database directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Database File"
        )
        
        if directory:
            success, message = path_manager.set_custom_database_path(directory)
            if success:
                # Log path change
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "changed database path", directory)
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Database Path Changed",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_browse_themes(self):
        """Browse for custom themes directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Themes File"
        )
        
        if directory:
            success, message = path_manager.set_custom_themes_path(directory)
            if success:
                # Log path change
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "changed themes path", directory)
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Themes Path Changed",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_reset_config(self):
        """Reset config to default location"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset config file to default location?\n\n"
            "Your custom config file will remain in its current location.\n"
            "The app will use the default config after restart.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = path_manager.reset_config_to_default()
            if success:
                # Log reset
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "reset config path", "To default location")
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Config Reset",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_reset_database(self):
        """Reset database to default location"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset database file to default location?\n\n"
            "Your custom database file will remain in its current location.\n"
            "The app will use the default database after restart.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = path_manager.reset_database_to_default()
            if success:
                # Log reset
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "reset database path", "To default location")
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Database Reset",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_reset_themes(self):
        """Reset themes to default location"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset themes file to default location?\n\n"
            "Your custom themes file will remain in its current location.\n"
            "The app will use the default themes after restart.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = path_manager.reset_themes_to_default()
            if success:
                # Log reset
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "reset themes path", "To default location")
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Themes Reset",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_restore_config(self):
        """Restore config to default settings"""
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            "Restore config file to default settings?\n\n"
            "This will overwrite your current config with default values.\n"
            "Your themes and other data will not be affected.\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = path_manager.restore_default_config()
            if success:
                # Log restore
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "restored config", "To default settings")
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"{message}"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_restore_database(self):
        """Restore database to default state"""
        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            "Restore database to default state?\n\n"
            "⚠ WARNING: This will DELETE all your data!\n"
            "• All tasks, notes, habits, expenses will be lost\n"
            "• A backup will be created automatically\n\n"
            "This action cannot be undone!\n\n"
            "Are you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Double confirmation
            reply2 = QMessageBox.warning(
                self,
                "Final Confirmation",
                "This is your last chance!\n\n"
                "Restore database and DELETE ALL DATA?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply2 == QMessageBox.StandardButton.Yes:
                success, message = path_manager.restore_default_database()
                if success:
                    # Log restore
                    from src.core.activity_logger import activity_logger
                    activity_logger.log("Settings", "restored database", "To default state")
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"{message}"
                    )
                else:
                    QMessageBox.critical(self, "Error", message)
    
    def on_browse_logs(self):
        """Browse for custom logs directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Logs"
        )
        
        if directory:
            success, message = path_manager.set_custom_logs_path(directory)
            if success:
                # Log path change
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "changed logs path", directory)
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Logs Path Changed",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_reset_logs(self):
        """Reset logs to default location"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset logs directory to default location?\n\n"
            "Your custom logs will remain in their current location.\n"
            "The app will use the default logs directory after restart.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = path_manager.reset_logs_to_default()
            if success:
                # Log reset
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "reset logs path", "To default location")
                
                # Show restart dialog
                self.show_restart_dialog(
                    "Logs Reset",
                    f"{message}\n\n"
                    "Restart Now: Apply changes immediately and restart the application\n"
                    "Restart Later: Changes will take effect on next manual restart"
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def show_restart_dialog(self, title, message):
        """Show dialog with Restart Now and Restart Later options"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        restart_now_btn = msg_box.addButton("Restart Now", QMessageBox.ButtonRole.AcceptRole)
        restart_later_btn = msg_box.addButton("Restart Later", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == restart_now_btn:
            # Trigger restart
            from src.core.config import config
            config.signals.restart_requested.emit()
        else:
            # Just refresh UI
            self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI to show updated paths"""
        # Clear and rebuild
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.setup_ui()
