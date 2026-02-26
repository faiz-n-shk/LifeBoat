"""
Advanced Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt

from src.core.config import config


class AdvancedSection(QWidget):
    """Advanced settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup advanced settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
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
        
        # Recent Activity Mode
        activity_label = QLabel("Recent Activity Display:")
        activity_label.setProperty("class", "section-label")
        layout.addWidget(activity_label)
        
        from PyQt6.QtWidgets import QComboBox
        activity_layout = QHBoxLayout()
        activity_desc = QLabel("Show activities from:")
        activity_layout.addWidget(activity_desc)
        
        self.activity_combo = QComboBox()
        self.activity_combo.addItems(["Today Only", "Last 7 Days (Standard)", "Disabled"])
        
        # Map config values to combo box indices
        activity_mode = config.get('advanced.recent_activity_mode', 'standard')
        mode_map = {'today': 0, 'standard': 1, 'none': 2}
        self.activity_combo.setCurrentIndex(mode_map.get(activity_mode, 1))
        self.activity_combo.currentIndexChanged.connect(self.on_value_changed)
        activity_layout.addWidget(self.activity_combo)
        activity_layout.addStretch()
        
        layout.addLayout(activity_layout)
        
        # Activity info label
        activity_info = QLabel("Controls what recent activities are shown on the Dashboard.")
        activity_info.setProperty("class", "secondary-text")
        activity_info.setWordWrap(True)
        layout.addWidget(activity_info)
        
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
        """Apply advanced changes"""
        # Store scroll position before applying changes
        scroll_area = self.get_scroll_area()
        scroll_pos = scroll_area.verticalScrollBar().value() if scroll_area else 0
        
        # Track changes for logging
        changes = []
        
        # Save debug buttons setting
        old_debug = config.get('advanced.show_debug_buttons')
        new_debug = self.debug_check.isChecked()
        if old_debug != new_debug:
            changes.append(f"Debug buttons: {'enabled' if new_debug else 'disabled'}")
        config.set('advanced.show_debug_buttons', new_debug)
        
        # Save recent activity mode
        mode_map = {0: 'today', 1: 'standard', 2: 'none'}
        old_activity = config.get('advanced.recent_activity_mode', 'standard')
        new_activity = mode_map[self.activity_combo.currentIndex()]
        if old_activity != new_activity:
            mode_names = {'today': 'Today Only', 'standard': 'Last 7 Days', 'none': 'Disabled'}
            changes.append(f"Recent activity: {mode_names[new_activity]}")
        config.set('advanced.recent_activity_mode', new_activity)
        
        if config.save(log_changes=False):
            # Log changes if any
            if changes:
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "updated advanced", ", ".join(changes))
            
            # Emit signal to reload UI with new advanced settings
            config.signals.advanced_changed.emit()
            
            # Restore scroll position after UI refresh
            if scroll_area:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, lambda: scroll_area.verticalScrollBar().setValue(scroll_pos))
            
            self.apply_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
            # Show success notification
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Success",
                "Advanced settings applied successfully!"
            )
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save advanced settings."
            )
    
    def on_cancel(self):
        """Cancel advanced changes and revert to saved values"""
        # Reload values from config
        self.debug_check.setChecked(config.get('advanced.show_debug_buttons', False))
        
        # Reload activity mode
        activity_mode = config.get('advanced.recent_activity_mode', 'standard')
        mode_map = {'today': 0, 'standard': 1, 'none': 2}
        self.activity_combo.setCurrentIndex(mode_map.get(activity_mode, 1))
        
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
