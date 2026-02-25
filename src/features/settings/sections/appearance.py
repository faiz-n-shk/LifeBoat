"""
Appearance Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt

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
        self.font_combo.addItems([
            "Segoe UI", "Arial", "Helvetica", "Calibri",
            "Verdana", "Tahoma", "Consolas"
        ])
        current_font = config.get('appearance.font_family', 'Segoe UI')
        self.font_combo.setCurrentText(current_font)
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        font_layout.addWidget(self.font_combo, 1)
        
        layout.addLayout(font_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_label = QLabel("Font Size:")
        size_label.setFixedWidth(150)
        size_layout.addWidget(size_label)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 20)
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
