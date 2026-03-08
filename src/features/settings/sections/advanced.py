"""
Advanced Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt
from src.shared.dialogs import NoScrollComboBox

from src.core.config import config


class AdvancedSection(QWidget):
    """Advanced settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup advanced settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Database Management Group
        db_group = QLabel("Database Management")
        db_group.setProperty("class", "section-label")
        layout.addWidget(db_group)
        
        # Auto-update database checkbox
        auto_update_layout = QHBoxLayout()
        self.auto_update_db_check = QCheckBox("Auto-update database on app updates")
        self.auto_update_db_check.setChecked(config.get('advanced.auto_update_database', True))
        self.auto_update_db_check.stateChanged.connect(self.on_value_changed)
        auto_update_layout.addWidget(self.auto_update_db_check)
        auto_update_layout.addStretch()
        layout.addLayout(auto_update_layout)
        
        # Info label for auto-update
        auto_info = QLabel("Automatically runs database migrations when the app is updated to ensure compatibility.")
        auto_info.setProperty("class", "secondary-text")
        auto_info.setWordWrap(True)
        layout.addWidget(auto_info)
        
        # Manual update button
        update_db_layout = QHBoxLayout()
        self.update_db_btn = QPushButton("Update Database Now")
        self.update_db_btn.setFixedWidth(200)
        self.update_db_btn.clicked.connect(self.on_update_database)
        update_db_layout.addWidget(self.update_db_btn)
        
        # Database version info
        self.db_version_label = QLabel()
        self.db_version_label.setProperty("class", "secondary-text")
        self.update_db_version_display()
        update_db_layout.addWidget(self.db_version_label)
        update_db_layout.addStretch()
        layout.addLayout(update_db_layout)
        
        # Info label for manual update
        manual_info = QLabel("Manually run database migrations to fix schema issues or update to the latest structure.")
        manual_info.setProperty("class", "secondary-text")
        manual_info.setWordWrap(True)
        layout.addWidget(manual_info)
        
        # Separator
        layout.addSpacing(10)
        
        # Debug Settings Group
        debug_group = QLabel("Debug Settings")
        debug_group.setProperty("class", "section-label")
        layout.addWidget(debug_group)
        
        # Debug buttons toggle
        debug_layout = QHBoxLayout()
        self.debug_check = QCheckBox("Show debug buttons (Reload/Restart)")
        self.debug_check.setChecked(config.get('advanced.show_debug_buttons', False))
        self.debug_check.stateChanged.connect(self.on_value_changed)
        debug_layout.addWidget(self.debug_check)
        debug_layout.addStretch()
        
        layout.addLayout(debug_layout)
        
        # Info label
        info_label = QLabel("Debug buttons appear in the navigation sidebar for quick reload/restart.")
        info_label.setProperty("class", "secondary-text")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Separator
        layout.addSpacing(10)
        
        # Log Rotation Group
        log_rotation_label = QLabel("Log File Management")
        log_rotation_label.setProperty("class", "section-label")
        layout.addWidget(log_rotation_label)
        
        from PyQt6.QtWidgets import QSpinBox
        log_rotation_layout = QHBoxLayout()
        log_rotation_desc = QLabel("Create new log file:")
        log_rotation_desc.setFixedWidth(150)
        log_rotation_layout.addWidget(log_rotation_desc)
        
        # Preset combo box
        self.log_rotation_combo = NoScrollComboBox()
        self.log_rotation_combo.addItems([
            "Every App Startup",
            "After 1 Day",
            "After 2 Days",
            "After 3 Days",
            "After 1 Week",
            "Custom"
        ])
        self.log_rotation_combo.setFixedWidth(180)
        log_rotation_layout.addWidget(self.log_rotation_combo)
        
        # Custom hours spinner (hidden by default)
        self.log_rotation_spin = QSpinBox()
        self.log_rotation_spin.setMinimum(1)
        self.log_rotation_spin.setMaximum(168)  # Max 1 week
        self.log_rotation_spin.setSuffix(" hours")
        self.log_rotation_spin.setFixedWidth(120)
        self.log_rotation_spin.setVisible(False)  # Hidden by default
        log_rotation_layout.addWidget(self.log_rotation_spin)
        
        log_rotation_layout.addStretch()
        layout.addLayout(log_rotation_layout)
        
        # Log rotation info label
        log_rotation_info = QLabel(
            "Controls when a new log file is created. 'Every App Startup' creates a new log each time (like before). "
            "Other options reuse 'latest.log' if restarted within the time period, then archive it with a timestamp."
            "and a new file is created. Lower values create more log files but keep them smaller."
        )
        log_rotation_info.setProperty("class", "secondary-text")
        log_rotation_info.setWordWrap(True)
        layout.addWidget(log_rotation_info)
        
        # Separator
        layout.addSpacing(10)
        
        # Recent Activity Group
        activity_label = QLabel("Recent Activity Display")
        activity_label.setProperty("class", "section-label")
        layout.addWidget(activity_label)
        
        from PyQt6.QtWidgets import QComboBox
        activity_layout = QHBoxLayout()
        activity_desc = QLabel("Show activities from:")
        activity_desc.setFixedWidth(150)
        activity_layout.addWidget(activity_desc)
        
        self.activity_combo = NoScrollComboBox()
        self.activity_combo.addItems([
            "Current Session",
            "Today (24 hours)",
            "Last 3 Days",
            "Last 7 Days (Standard)",
            "Last 30 Days",
            "All Time",
            "Disabled"
        ])
        
        # Map config values to combo box indices
        activity_mode = config.get('advanced.recent_activity_mode', 'all')
        mode_map = {
            'session': 0,
            'today': 1,
            '3days': 2,
            'standard': 3,
            '30days': 4,
            'all': 5,
            'none': 6
        }
        self.activity_combo.setCurrentIndex(mode_map.get(activity_mode, 5))
        self.activity_combo.currentIndexChanged.connect(self.on_value_changed)
        activity_layout.addWidget(self.activity_combo)
        activity_layout.addStretch()
        
        layout.addLayout(activity_layout)
        
        # Activity info label
        activity_info = QLabel("Controls what recent activities are shown on the Dashboard. 'Current Session' shows activities since the app was started.")
        activity_info.setProperty("class", "secondary-text")
        activity_info.setWordWrap(True)
        layout.addWidget(activity_info)
        
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
        
        # Connect signals AFTER buttons are created
        self.log_rotation_combo.currentIndexChanged.connect(self.on_log_rotation_preset_changed)
        self.log_rotation_spin.valueChanged.connect(self.on_value_changed)
        
        # Load initial values AFTER everything is set up
        self.load_log_rotation_setting()
    
    def on_value_changed(self):
        """Handle any value change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_log_rotation_preset_changed(self, index):
        """Handle log rotation preset change"""
        # Show/hide custom spinner based on selection
        is_custom = (index == 5)  # "Custom" is index 5
        self.log_rotation_spin.setVisible(is_custom)
        
        # Enable apply button
        self.on_value_changed()
    
    def load_log_rotation_setting(self):
        """Load log rotation setting from config and set UI"""
        hours = config.get('advanced.log_rotation_hours', 120)  # Default 5 days
        
        # Block signals while loading to prevent triggering on_value_changed
        self.log_rotation_combo.blockSignals(True)
        self.log_rotation_spin.blockSignals(True)
        
        # Map hours to preset index
        preset_map = {
            0: 0,    # Every App Startup
            24: 1,   # After 1 Day
            48: 2,   # After 2 Days
            72: 3,   # After 3 Days
            168: 4   # After 1 Week
        }
        
        if hours in preset_map:
            self.log_rotation_combo.setCurrentIndex(preset_map[hours])
            self.log_rotation_spin.setVisible(False)
        else:
            # Custom value
            self.log_rotation_combo.setCurrentIndex(5)  # "Custom"
            self.log_rotation_spin.setValue(hours)
            self.log_rotation_spin.setVisible(True)
        
        # Unblock signals
        self.log_rotation_combo.blockSignals(False)
        self.log_rotation_spin.blockSignals(False)
    
    def get_log_rotation_hours(self):
        """Get the selected log rotation hours value"""
        index = self.log_rotation_combo.currentIndex()
        
        # Map preset index to hours
        preset_hours = {
            0: 0,    # Every App Startup
            1: 24,   # After 1 Day
            2: 48,   # After 2 Days
            3: 72,   # After 3 Days
            4: 168,  # After 1 Week
            5: self.log_rotation_spin.value()  # Custom
        }
        
        return preset_hours.get(index, 120)
    
    def update_db_version_display(self):
        """Update the database version display label"""
        from src.core.database_migrations import get_database_version
        from src.core.constants import APP_VERSION
        
        db_version = get_database_version()
        if db_version == APP_VERSION:
            self.db_version_label.setText(f"✓ Database version: {db_version} (up to date)")
        else:
            self.db_version_label.setText(f"⚠ Database version: {db_version} (app version: {APP_VERSION})")
    
    def on_update_database(self):
        """Handle database update button click"""
        from src.shared.dialogs import create_message_box, show_critical
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm action
        result = create_message_box(
            self,
            "Update Database",
            "This will run database migrations to update the schema.\n\n"
            "A backup will be created automatically.\n\n"
            "Do you want to continue?",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button during migration
        self.update_db_btn.setEnabled(False)
        self.update_db_btn.setText("Updating...")
        
        try:
            # Close any open database connections first
            from src.core.database import db
            if not db.is_closed():
                db.close()
            
            # Create backup first
            from src.core.database_migrations import backup_database, run_migrations
            
            backup_success, backup_path = backup_database()
            if not backup_success:
                show_critical(
                    self,
                    "Backup Failed",
                    f"Could not create database backup:\n{backup_path}\n\nMigration cancelled."
                )
                return
            
            # Run migrations
            success, message = run_migrations(force=True)
            
            if success:
                # Update version display
                self.update_db_version_display()
                
                # Show success with restart options
                restart_result = create_message_box(
                    self,
                    "Database Updated Successfully",
                    f"{message}\n\nBackup saved to:\n{backup_path}\n\n"
                    "A restart is recommended to apply all changes.\n\n"
                    "Would you like to restart now?",
                    QMessageBox.Icon.Information,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if restart_result == QMessageBox.StandardButton.Yes:
                    # Trigger restart
                    from src.core.config import config
                    config.signals.restart_requested.emit()
            else:
                show_critical(
                    self,
                    "Migration Failed",
                    f"{message}\n\nYour database backup is at:\n{backup_path}"
                )
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Database update error: {error_details}")
            show_critical(
                self,
                "Error",
                f"An error occurred during database update:\n{str(e)}\n\n"
                "The app will need to be restarted for changes to take effect."
            )
        
        finally:
            # Re-enable button
            self.update_db_btn.setEnabled(True)
            self.update_db_btn.setText("Update Database Now")
    
    def on_apply(self):
        """Apply advanced changes"""
        # Store scroll position before applying changes
        scroll_area = self.get_scroll_area()
        scroll_pos = scroll_area.verticalScrollBar().value() if scroll_area else 0
        
        # Track changes for logging
        changes = []
        
        # Save auto-update database setting
        old_auto_db = config.get('advanced.auto_update_database', True)
        new_auto_db = self.auto_update_db_check.isChecked()
        if old_auto_db != new_auto_db:
            changes.append(f"Auto-update database: {'enabled' if new_auto_db else 'disabled'}")
        config.set('advanced.auto_update_database', new_auto_db)
        
        # Save debug buttons setting
        old_debug = config.get('advanced.show_debug_buttons')
        new_debug = self.debug_check.isChecked()
        if old_debug != new_debug:
            changes.append(f"Debug buttons: {'enabled' if new_debug else 'disabled'}")
        config.set('advanced.show_debug_buttons', new_debug)
        
        # Save log rotation hours
        old_rotation = config.get('advanced.log_rotation_hours', 120)
        new_rotation = self.get_log_rotation_hours()
        if old_rotation != new_rotation:
            if new_rotation == 0:
                changes.append("Log rotation: Every app startup")
            elif new_rotation == 24:
                changes.append("Log rotation: After 1 day")
            elif new_rotation == 48:
                changes.append("Log rotation: After 2 days")
            elif new_rotation == 72:
                changes.append("Log rotation: After 3 days")
            elif new_rotation == 168:
                changes.append("Log rotation: After 1 week")
            else:
                changes.append(f"Log rotation: After {new_rotation} hours")
        config.set('advanced.log_rotation_hours', new_rotation)
        
        # Save recent activity mode
        mode_map = {0: 'session', 1: 'today', 2: '3days', 3: 'standard', 4: '30days', 5: 'all', 6: 'none'}
        old_activity = config.get('advanced.recent_activity_mode', 'all')
        new_activity = mode_map[self.activity_combo.currentIndex()]
        if old_activity != new_activity:
            mode_names = {
                'session': 'Current Session',
                'today': 'Today (24 hours)',
                '3days': 'Last 3 Days',
                'standard': 'Last 7 Days',
                '30days': 'Last 30 Days',
                'all': 'All Time',
                'none': 'Disabled'
            }
            changes.append(f"Recent activity: {mode_names[new_activity]}")
        config.set('advanced.recent_activity_mode', new_activity)
        
        if config.save(log_changes=False):
            # Log changes if any
            if changes:
                from src.core.activity_logger import activity_logger
                from src.core.activity_formatter import format_settings_log
                action, details = format_settings_log('advanced', changes)
                activity_logger.log("Settings", action, details)
            
            # Emit signal to reload UI with new advanced settings
            config.signals.advanced_changed.emit()
            
            # Restore scroll position after UI refresh
            if scroll_area:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, lambda: scroll_area.verticalScrollBar().setValue(scroll_pos))
            
            self.apply_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
            # Show success notification
            from src.shared.dialogs import show_information
            show_information(
                self,
                "Success",
                "Advanced settings applied successfully!"
            )
        else:
            from src.shared.dialogs import show_warning
            show_warning(
                self,
                "Error",
                "Failed to save advanced settings."
            )
    
    def on_cancel(self):
        """Cancel advanced changes and revert to saved values"""
        # Reload auto-update database setting
        self.auto_update_db_check.setChecked(config.get('advanced.auto_update_database', True))
        
        # Reload values from config
        self.debug_check.setChecked(config.get('advanced.show_debug_buttons', False))
        
        # Reload log rotation setting
        self.load_log_rotation_setting()
        
        # Reload activity mode
        activity_mode = config.get('advanced.recent_activity_mode', 'all')
        mode_map = {
            'session': 0,
            'today': 1,
            '3days': 2,
            'standard': 3,
            '30days': 4,
            'all': 5,
            'none': 6
        }
        self.activity_combo.setCurrentIndex(mode_map.get(activity_mode, 5))
        
        # Disable buttons
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
    
    def get_scroll_area(self):
        """Find the parent scroll area widget"""
        from PyQt6.QtWidgets import QScrollArea
        widget = self.parent()
        while widget:
            if isinstance(widget.parent(), QScrollArea):
                return widget.parent()
            widget = widget.parent()
        return None
