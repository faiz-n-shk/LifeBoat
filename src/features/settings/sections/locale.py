"""
Locale Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt

from src.core.config import config
from src.shared.formatters import get_available_currencies, get_currency_code


class LocaleSection(QWidget):
    """Locale and format settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup locale settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Date format
        date_layout = QHBoxLayout()
        date_label = QLabel("Date Format:")
        date_label.setFixedWidth(150)
        date_layout.addWidget(date_label)
        
        self.date_input = QLineEdit()
        self.date_input.setText(config.get('datetime.date_format', '%d-%m-%Y'))
        self.date_input.setPlaceholderText("%d-%m-%Y")
        date_layout.addWidget(self.date_input, 1)
        
        layout.addLayout(date_layout)
        
        # Time mode
        time_layout = QHBoxLayout()
        time_label = QLabel("Time Mode:")
        time_label.setFixedWidth(150)
        time_layout.addWidget(time_label)
        
        self.time_combo = QComboBox()
        self.time_combo.addItems(["12hr", "24hr"])
        self.time_combo.setCurrentText(config.get('datetime.time_mode', '12hr'))
        time_layout.addWidget(self.time_combo, 1)
        
        layout.addLayout(time_layout)
        
        # Week start
        week_layout = QHBoxLayout()
        week_label = QLabel("Week Starts On:")
        week_label.setFixedWidth(150)
        week_layout.addWidget(week_label)
        
        self.week_combo = QComboBox()
        self.week_combo.addItems(["Monday", "Sunday"])
        self.week_combo.setCurrentText(config.get('datetime.week_start', 'Monday'))
        week_layout.addWidget(self.week_combo, 1)
        
        layout.addLayout(week_layout)
        
        # Currency symbol (dropdown)
        currency_layout = QHBoxLayout()
        currency_label = QLabel("Currency:")
        currency_label.setFixedWidth(150)
        currency_layout.addWidget(currency_label)
        
        self.currency_combo = QComboBox()
        currencies = get_available_currencies()
        self.currency_combo.addItems(currencies)
        current_symbol = config.get('currency.symbol', '₹')
        if current_symbol in currencies:
            self.currency_combo.setCurrentText(current_symbol)
        currency_layout.addWidget(self.currency_combo)
        
        # Show currency code (read-only)
        self.code_label = QLabel()
        self.code_label.setStyleSheet("color: #b0b0b0; margin-left: 10px;")
        self.update_currency_code()
        self.currency_combo.currentTextChanged.connect(self.update_currency_code)
        currency_layout.addWidget(self.code_label)
        
        currency_layout.addStretch()
        
        layout.addLayout(currency_layout)
        
        # Currency position
        position_layout = QHBoxLayout()
        position_label = QLabel("Currency Position:")
        position_label.setFixedWidth(150)
        position_layout.addWidget(position_label)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(["prefix", "suffix"])
        self.position_combo.setCurrentText(config.get('currency.position', 'prefix'))
        position_layout.addWidget(self.position_combo, 1)
        
        layout.addLayout(position_layout)
        
        # Decimal places
        decimal_layout = QHBoxLayout()
        decimal_label = QLabel("Decimal Places:")
        decimal_label.setFixedWidth(150)
        decimal_layout.addWidget(decimal_label)
        
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(0, 4)
        self.decimal_spin.setValue(config.get('currency.decimal_places', 2))
        decimal_layout.addWidget(self.decimal_spin)
        decimal_layout.addStretch()
        
        layout.addLayout(decimal_layout)
        
        # Apply button
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.on_apply)
        apply_layout.addWidget(apply_btn)
        
        layout.addLayout(apply_layout)
        
        self.setLayout(layout)
    
    def update_currency_code(self):
        """Update currency code label"""
        symbol = self.currency_combo.currentText()
        code = get_currency_code(symbol)
        self.code_label.setText(f"({code})")
    
    def on_apply(self):
        """Apply locale changes"""
        symbol = self.currency_combo.currentText()
        code = get_currency_code(symbol)
        
        # Save to config
        config.set('datetime.date_format', self.date_input.text())
        config.set('datetime.time_mode', self.time_combo.currentText())
        config.set('datetime.week_start', self.week_combo.currentText())
        config.set('currency.symbol', symbol)
        config.set('currency.code', code)
        config.set('currency.position', self.position_combo.currentText())
        config.set('currency.decimal_places', self.decimal_spin.value())
        
        if config.save():
            # Emit signal to reload formatters and UI
            config.signals.locale_changed.emit()
            
            # Show success notification
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Success",
                "Locale settings applied successfully!"
            )
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save locale settings."
            )
