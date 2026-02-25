"""
Appearance Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSpinBox, QCheckBox, QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QScreen
import os
import shutil

from src.core.config import config


class AppearanceSection(QWidget):
    """Appearance settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_resolutions = []
        self.monitors = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup appearance settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Font family
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Family:")
        font_label.setFixedWidth(150)
        font_layout.addWidget(font_label)
        
        self.font_combo = QComboBox()
        self.load_available_fonts()
        current_font = config.get('appearance.font_family', 'Segoe UI')
        if current_font in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
            self.font_combo.setCurrentText(current_font)
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        font_layout.addWidget(self.font_combo, 1)
        
        # Import font button
        import_btn = QPushButton("Import Font")
        import_btn.clicked.connect(self.on_import_font)
        font_layout.addWidget(import_btn)
        
        layout.addLayout(font_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_label = QLabel("Font Size:")
        size_label.setFixedWidth(150)
        size_layout.addWidget(size_label)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(5, 20)  # min max font size
        self.size_spin.setValue(config.get('appearance.font_size', 13))
        self.size_spin.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        
        layout.addLayout(size_layout)
        
        # Animations
        anim_layout = QHBoxLayout()
        self.animations_check = QCheckBox("Enable animations")
        self.animations_check.setChecked(config.get('appearance.enable_animations', True))
        self.animations_check.stateChanged.connect(self.on_animations_changed)
        anim_layout.addWidget(self.animations_check)
        anim_layout.addStretch()
        
        layout.addLayout(anim_layout)
        
        # Detect monitors and resolutions
        self.detect_monitors()
        
        # Monitor selection (only show if multiple monitors)
        if len(self.monitors) > 1:
            monitor_layout = QHBoxLayout()
            monitor_label = QLabel("Monitor:")
            monitor_label.setFixedWidth(150)
            monitor_layout.addWidget(monitor_label)
            
            self.monitor_combo = QComboBox()
            for i, monitor in enumerate(self.monitors):
                self.monitor_combo.addItem(f"Monitor {i + 1} ({monitor['width']}x{monitor['height']})")
            
            current_monitor = config.get('window.monitor', 0)
            if current_monitor < len(self.monitors):
                self.monitor_combo.setCurrentIndex(current_monitor)
            
            self.monitor_combo.currentIndexChanged.connect(self.on_monitor_changed)
            monitor_layout.addWidget(self.monitor_combo, 1)
            
            layout.addLayout(monitor_layout)
        
        # Resolution
        res_layout = QHBoxLayout()
        res_label = QLabel("Window Resolution:")
        res_label.setFixedWidth(150)
        res_layout.addWidget(res_label)
        
        self.resolution_combo = QComboBox()
        self.load_available_resolutions()
        
        # Get current resolution setting
        current_res = config.get('window.resolution', 'custom')
        self.set_resolution_combo(current_res)
        self.resolution_combo.currentIndexChanged.connect(self.on_resolution_changed)
        res_layout.addWidget(self.resolution_combo, 1)
        
        layout.addLayout(res_layout)
        
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
    
    def on_font_changed(self, font_family: str):
        """Handle font change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_size_changed(self, size: int):
        """Handle size change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_animations_changed(self, state):
        """Handle animations toggle"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_monitor_changed(self, index):
        """Handle monitor change"""
        # Reload resolutions for selected monitor
        self.load_available_resolutions()
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_resolution_changed(self, index):
        """Handle resolution change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_apply(self):
        """Apply appearance changes"""
        # Store scroll position before applying changes
        scroll_area = self.get_scroll_area()
        scroll_pos = scroll_area.verticalScrollBar().value() if scroll_area else 0
        
        # Save to config
        config.set('appearance.font_family', self.font_combo.currentText())
        config.set('appearance.font_size', self.size_spin.value())
        config.set('appearance.enable_animations', self.animations_check.isChecked())
        
        # Save monitor selection if multiple monitors
        if len(self.monitors) > 1 and hasattr(self, 'monitor_combo'):
            config.set('window.monitor', self.monitor_combo.currentIndex())
        
        # Save resolution
        if self.resolution_combo.currentIndex() >= 0:
            res_value = self.available_resolutions[self.resolution_combo.currentIndex()][1]
            config.set('window.resolution', res_value)
            
            # Apply resolution if not custom
            if res_value != 'custom':
                self.apply_resolution(res_value)
        
        if config.save():
            # Emit signal to reload UI
            config.signals.appearance_changed.emit()
            
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
                "Appearance settings applied successfully!"
            )
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save appearance settings."
            )
    
    def get_scroll_area(self):
        """Find the parent scroll area widget"""
        from PyQt6.QtWidgets import QScrollArea
        widget = self.parent()
        while widget:
            if isinstance(widget.parent(), QScrollArea):
                return widget.parent()
            widget = widget.parent()
        return None
    
    def on_cancel(self):
        """Cancel appearance changes and revert to saved values"""
        # Reload values from config
        current_font = config.get('appearance.font_family', 'Segoe UI')
        if current_font in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
            self.font_combo.setCurrentText(current_font)
        
        self.size_spin.setValue(config.get('appearance.font_size', 13))
        self.animations_check.setChecked(config.get('appearance.enable_animations', True))
        
        # Reload resolution
        current_res = config.get('window.resolution', 'custom')
        self.set_resolution_combo(current_res)
        
        # Disable buttons
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
    
    def load_available_fonts(self):
        """Load system fonts and custom fonts from assets/fonts"""
        fonts = set()
        
        # Add default system fonts
        default_fonts = [
            "Segoe UI", "Arial", "Helvetica", "Calibri",
            "Verdana", "Tahoma", "Consolas", "Times New Roman",
            "Courier New", "Georgia"
        ]
        fonts.update(default_fonts)
        
        # Load custom fonts from assets/fonts directory
        fonts_dir = "assets/fonts"
        if os.path.exists(fonts_dir):
            for filename in os.listdir(fonts_dir):
                if filename.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(fonts_dir, filename)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        fonts.update(font_families)
        
        # Sort and add to combo box
        sorted_fonts = sorted(fonts)
        self.font_combo.addItems(sorted_fonts)
    
    def on_import_font(self):
        """Import a custom font file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Font File",
            "",
            "Font Files (*.ttf *.otf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Create fonts directory if it doesn't exist
                fonts_dir = "assets/fonts"
                os.makedirs(fonts_dir, exist_ok=True)
                
                # Copy font file to assets/fonts
                filename = os.path.basename(file_path)
                dest_path = os.path.join(fonts_dir, filename)
                
                if os.path.exists(dest_path):
                    reply = QMessageBox.question(
                        self,
                        "Font Exists",
                        f"Font '{filename}' already exists. Replace it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                shutil.copy2(file_path, dest_path)
                
                # Load the font
                font_id = QFontDatabase.addApplicationFont(dest_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        font_name = font_families[0]
                        
                        # Add to combo box if not already there
                        if self.font_combo.findText(font_name) == -1:
                            self.font_combo.addItem(font_name)
                        
                        # Select the new font
                        self.font_combo.setCurrentText(font_name)
                        self.apply_btn.setEnabled(True)
                        
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Font '{font_name}' imported successfully!\n\nClick 'Apply Changes' to use it."
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "Failed to load font family from file."
                        )
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to load font file. The file may be corrupted or invalid."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to import font: {str(e)}"
                )

    def detect_monitors(self):
        """Detect available monitors and their resolutions"""
        self.monitors = []
        app = QApplication.instance()
        
        if app:
            screens = app.screens()
            for screen in screens:
                geometry = screen.geometry()
                self.monitors.append({
                    'width': geometry.width(),
                    'height': geometry.height(),
                    'screen': screen
                })
    
    def load_available_resolutions(self):
        """Load resolutions available for the selected monitor"""
        self.available_resolutions = [("Custom", "custom")]
        
        # Get selected monitor
        monitor_index = 0
        if len(self.monitors) > 1 and hasattr(self, 'monitor_combo'):
            monitor_index = self.monitor_combo.currentIndex()
        
        if monitor_index < len(self.monitors):
            max_width = self.monitors[monitor_index]['width']
            max_height = self.monitors[monitor_index]['height']
            
            # Comprehensive resolution list organized by aspect ratio
            # Format: (width, height, "Name", "Aspect Ratio")
            all_resolutions = [
                # 4:3 Aspect Ratio
                (640, 480, "VGA", "4:3"),
                (800, 600, "SVGA", "4:3"),
                (1024, 768, "XGA", "4:3"),
                (1152, 864, "XGA+", "4:3"),
                (1280, 960, "SXGA-", "4:3"),
                (1400, 1080, "SXGA+", "4:3"),
                (1600, 1200, "UXGA", "4:3"),
                (1920, 1440, "TXGA", "4:3"),
                (2048, 1536, "QXGA", "4:3"),
                
                # 5:4 Aspect Ratio
                (1280, 1024, "SXGA", "5:4"),
                (2560, 2048, "QSXGA", "5:4"),
                
                # 16:10 Aspect Ratio
                (1280, 800, "WXGA", "16:10"),
                (1440, 900, "WXGA+", "16:10"),
                (1680, 1050, "WSXGA+", "16:10"),
                (1920, 1200, "WUXGA", "16:10"),
                (2560, 1600, "WQXGA", "16:10"),
                (3840, 2400, "WQUXGA", "16:10"),
                
                # 16:9 Aspect Ratio (Most Common)
                (1280, 720, "HD", "16:9"),
                (1366, 768, "WXGA", "16:9"),
                (1600, 900, "HD+", "16:9"),
                (1920, 1080, "Full HD", "16:9"),
                (2560, 1440, "QHD/2K", "16:9"),
                (3200, 1800, "QHD+", "16:9"),
                (3840, 2160, "4K UHD", "16:9"),
                (5120, 2880, "5K", "16:9"),
                (7680, 4320, "8K UHD", "16:9"),
                
                # 21:9 Ultrawide
                (2560, 1080, "UW-FHD", "21:9"),
                (3440, 1440, "UW-QHD", "21:9"),
                (5120, 2160, "UW-5K", "21:9"),
                
                # 32:9 Super Ultrawide
                (3840, 1080, "DFHD", "32:9"),
                (5120, 1440, "DQHD", "32:9"),
            ]
            
            # Group resolutions by aspect ratio
            grouped = {}
            for width, height, name, aspect in all_resolutions:
                if width <= max_width and height <= max_height:
                    if aspect not in grouped:
                        grouped[aspect] = []
                    grouped[aspect].append((width, height, name, aspect))
            
            # Add resolutions in order: 16:9, 16:10, 4:3, 5:4, 21:9, 32:9
            aspect_order = ["16:9", "16:10", "4:3", "5:4", "21:9", "32:9"]
            
            for aspect in aspect_order:
                if aspect in grouped:
                    for width, height, name, aspect_ratio in grouped[aspect]:
                        display_name = f"{width}x{height} ({name}) [{aspect_ratio}]"
                        self.available_resolutions.append(
                            (display_name, f"{width}x{height}")
                        )
        
        # Update combo box
        current_selection = self.resolution_combo.currentText() if hasattr(self, 'resolution_combo') else None
        self.resolution_combo.clear()
        
        for display_name, _ in self.available_resolutions:
            self.resolution_combo.addItem(display_name)
        
        # Restore selection if possible
        if current_selection:
            index = self.resolution_combo.findText(current_selection)
            if index >= 0:
                self.resolution_combo.setCurrentIndex(index)
    
    def set_resolution_combo(self, res_value: str):
        """Set resolution combo box to match the given resolution value"""
        for i, (_, value) in enumerate(self.available_resolutions):
            if value == res_value:
                self.resolution_combo.setCurrentIndex(i)
                return
        # Default to custom if not found
        self.resolution_combo.setCurrentIndex(0)
    
    def apply_resolution(self, res_value: str):
        """Apply the selected resolution to the main window"""
        if res_value == 'custom':
            return
        
        try:
            width, height = map(int, res_value.split('x'))
            
            # Get main window (QMainWindow)
            widget = self
            while widget.parent():
                widget = widget.parent()
                if hasattr(widget, 'programmatic_resize'):
                    # Found the main app window
                    widget.programmatic_resize = True
                    widget.resize(width, height)
                    
                    # Save to config
                    config.set('window.width', width)
                    config.set('window.height', height)
                    config.save()
                    break
        except Exception as e:
            print(f"Error applying resolution: {e}")
    
    def update_resolution_display(self):
        """Update resolution combo to show current state (called from main window)"""
        current_res = config.get('window.resolution', 'custom')
        self.set_resolution_combo(current_res)
