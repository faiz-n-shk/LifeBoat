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
        self.date_input.textChanged.connect(self.on_value_changed)
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
        self.time_combo.currentTextChanged.connect(self.on_value_changed)
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
        self.week_combo.currentTextChanged.connect(self.on_value_changed)
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
        self.currency_combo.currentTextChanged.connect(self.update_currency_code)
        self.currency_combo.currentTextChanged.connect(self.on_value_changed)
        currency_layout.addWidget(self.currency_combo)
        
        # Show currency code (read-only)
        self.code_label = QLabel()
        self.code_label.setProperty("class", "secondary-text")
        self.code_label.setStyleSheet("margin-left: 10px;")
        self.update_currency_code()
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
        self.position_combo.currentTextChanged.connect(self.on_value_changed)
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
        self.decimal_spin.valueChanged.connect(self.on_value_changed)
        decimal_layout.addWidget(self.decimal_spin)
        decimal_layout.addStretch()
        
        layout.addLayout(decimal_layout)
        
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
    
    def update_currency_code(self):
        """Update currency code label"""
        symbol = self.currency_combo.currentText()
        code = get_currency_code(symbol)
        self.code_label.setText(f"({code})")
    
    def on_value_changed(self):
        """Handle any value change"""
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_apply(self):
        """Apply locale changes"""
        # Store scroll position before applying changes
        scroll_area = self.get_scroll_area()
        scroll_pos = scroll_area.verticalScrollBar().value() if scroll_area else 0
        
        symbol = self.currency_combo.currentText()
        code = get_currency_code(symbol)
        
        # Track changes for logging
        changes = []
        
        # Save to config
        old_date_format = config.get('datetime.date_format')
        new_date_format = self.date_input.text()
        if old_date_format != new_date_format:
            changes.append(f"Date format: {old_date_format} → {new_date_format}")
        config.set('datetime.date_format', new_date_format)
        
        old_time_mode = config.get('datetime.time_mode')
        new_time_mode = self.time_combo.currentText()
        if old_time_mode != new_time_mode:
            changes.append(f"Time mode: {old_time_mode} → {new_time_mode}")
        config.set('datetime.time_mode', new_time_mode)
        
        old_week_start = config.get('datetime.week_start')
        new_week_start = self.week_combo.currentText()
        if old_week_start != new_week_start:
            changes.append(f"Week start: {old_week_start} → {new_week_start}")
        config.set('datetime.week_start', new_week_start)
        
        old_currency = config.get('currency.symbol')
        if old_currency != symbol:
            changes.append(f"Currency: {old_currency} → {symbol}")
        config.set('currency.symbol', symbol)
        config.set('currency.code', code)
        
        old_position = config.get('currency.position')
        new_position = self.position_combo.currentText()
        if old_position != new_position:
            changes.append(f"Currency position: {old_position} → {new_position}")
        config.set('currency.position', new_position)
        
        old_decimal = config.get('currency.decimal_places')
        new_decimal = self.decimal_spin.value()
        if old_decimal != new_decimal:
            changes.append(f"Decimal places: {old_decimal} → {new_decimal}")
        config.set('currency.decimal_places', new_decimal)
        
        if config.save(log_changes=False):
            # Log changes if any
            if changes:
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "updated locale", ", ".join(changes))
            
            # Emit signal to reload formatters and UI
            config.signals.locale_changed.emit()
            
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
                "Locale settings applied successfully!"
            )
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save locale settings."
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
        """Cancel locale changes and revert to saved values"""
        # Reload values from config
        self.date_input.setText(config.get('datetime.date_format', '%d-%m-%Y'))
        self.time_combo.setCurrentText(config.get('datetime.time_mode', '12hr'))
        self.week_combo.setCurrentText(config.get('datetime.week_start', 'Monday'))
        
        current_symbol = config.get('currency.symbol', '₹')
        currencies = get_available_currencies()
        if current_symbol in currencies:
            self.currency_combo.setCurrentText(current_symbol)
        
        self.position_combo.setCurrentText(config.get('currency.position', 'prefix'))
        self.decimal_spin.setValue(config.get('currency.decimal_places', 2))
        
        # Update currency code
        self.update_currency_code()
        
        # Disable buttons
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
