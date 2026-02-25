"""
Expense Dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QFormLayout, QDoubleSpinBox
)
from PyQt6.QtCore import QDate, QTime

from src.core.config import config
from src.shared.widgets import TimePicker


class ExpenseDialog(QDialog):
    """Dialog for creating/editing expense"""
    
    def __init__(self, parent=None, expense=None):
        super().__init__(parent)
        self.expense = expense
        self.is_edit = expense is not None
        self.setup_ui()
        
        if self.is_edit:
            self.load_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Edit Expense" if self.is_edit else "New Expense")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        
        # Set currency prefix from config
        currency_symbol = config.get('currency.symbol', '₹')
        self.amount_input.setPrefix(f"{currency_symbol} ")
        
        form.addRow("Amount:", self.amount_input)
        
        # Category
        self.category_combo = QComboBox()
        categories = config.get('categories.expenses', [])
        self.category_combo.addItems(categories)
        form.addRow("Category:", self.category_combo)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form.addRow("Description:", self.description_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        # Apply locale settings for calendar
        self.apply_locale_to_calendar()
        
        form.addRow("Date:", self.date_input)
        
        # Time
        self.time_picker = TimePicker(self)
        form.addRow("Time:", self.time_picker)
        
        # Payment method
        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("Cash, Card, UPI, etc.")
        form.addRow("Payment Method:", self.payment_input)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
    
    def load_data(self):
        """Load expense data"""
        self.amount_input.setValue(float(self.expense.amount))
        self.category_combo.setCurrentText(self.expense.category)
        if self.expense.description:
            self.description_input.setPlainText(self.expense.description)
        self.date_input.setDate(QDate(self.expense.date))
        if self.expense.time:
            time = QTime(self.expense.time)
            self.time_picker.set_time(time.hour(), time.minute())
        if self.expense.payment_method:
            self.payment_input.setText(self.expense.payment_method)
    
    def get_data(self):
        """Get form data"""
        hour, minute = self.time_picker.get_time()
        time_obj = QTime(hour, minute)
        
        return {
            'amount': self.amount_input.value(),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip() or None,
            'date': self.date_input.date().toPyDate(),
            'time': time_obj.toPyTime(),
            'payment_method': self.payment_input.text().strip() or None,
        }
    
    def apply_locale_to_calendar(self):
        """Apply locale settings to calendar widget"""
        from PyQt6.QtCore import Qt
        
        # Get week start setting
        week_start = config.get('datetime.week_start', 'Monday')
        
        # Get the calendar widget
        calendar = self.date_input.calendarWidget()
        if calendar:
            if week_start == 'Sunday':
                calendar.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
            else:
                calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
