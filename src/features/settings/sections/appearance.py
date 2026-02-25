"""
Appearance Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSpinBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
import os
import shutil

from src.core.config import config


class AppearanceSection(QWidget):
    """Appearance settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        
        # Apply button
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.on_apply)
        self.apply_btn.setEnabled(False)
        apply_layout.addWidget(self.apply_btn)
        
        layout.addLayout(apply_layout)
        
        self.setLayout(layout)
    
    def on_font_changed(self, font_family: str):
        """Handle font change"""
        self.apply_btn.setEnabled(True)
    
    def on_size_changed(self, size: int):
        """Handle size change"""
        self.apply_btn.setEnabled(True)
    
    def on_animations_changed(self, state):
        """Handle animations toggle"""
        self.apply_btn.setEnabled(True)
    
    def on_apply(self):
        """Apply appearance changes"""
        # Save to config
        config.set('appearance.font_family', self.font_combo.currentText())
        config.set('appearance.font_size', self.size_spin.value())
        config.set('appearance.enable_animations', self.animations_check.isChecked())
        
        if config.save():
            # Emit signal to reload UI
            config.signals.appearance_changed.emit()
            
            self.apply_btn.setEnabled(False)
            
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
