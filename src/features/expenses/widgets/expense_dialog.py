"""
Expense Dialog
"""
from PyQt6.QtWidgets import QLabel, QComboBox, QDoubleSpinBox, QLineEdit
from PyQt6.QtCore import QTime

from src.core.config import config
from src.shared.dialogs import BaseDialog


class ExpenseDialog(BaseDialog):
    """Dialog for creating/editing expense"""
    
    def __init__(self, parent=None, expense=None):
        self.expense = expense
        self.is_edit = expense is not None
        
        title = "Edit Expense" if self.is_edit else "New Expense"
        super().__init__(parent, title=title, width=450, height=550)
        
        self.setup_fields()
        
        if self.is_edit:
            self.load_data()
    
    def setup_fields(self):
        """Setup expense-specific fields"""
        # Amount
        amount_label = QLabel("Amount:")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        
        # Get decimal places from config
        decimal_places = config.get('currency.decimal_places', 2)
        self.amount_input.setDecimals(decimal_places)
        
        # Set currency prefix from config
        currency_symbol = config.get('currency.symbol', '₹')
        self.amount_input.setPrefix(f"{currency_symbol} ")
        
        self.layout.addWidget(amount_label)
        self.layout.addWidget(self.amount_input)
        
        # Category
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        categories = config.get('categories.expenses', [])
        self.category_combo.addItems(categories)
        self.layout.addWidget(category_label)
        self.layout.addWidget(self.category_combo)
        
        # Description
        self.add_description_field()
        
        # Date and time
        self.add_date_time_field()
        
        # Payment method
        payment_label = QLabel("Payment Method:")
        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("Cash, Card, UPI, etc. (optional)")
        self.layout.addWidget(payment_label)
        self.layout.addWidget(self.payment_input)
        
        # Buttons
        save_text = "Save" if self.is_edit else "Add Expense"
        self.add_buttons(save_text=save_text, on_save=self.on_save)
    
    def load_data(self):
        """Load expense data into form"""
        self.amount_input.setValue(float(self.expense.amount))
        self.category_combo.setCurrentText(self.expense.category)
        if self.expense.description:
            self.description_input.setPlainText(self.expense.description)
        
        # Set date
        self.date_input.setDate(self.expense.date)
        
        # Set time
        if self.expense.time:
            time = QTime(self.expense.time)
            self.time_input.setTime(time)
        
        if self.expense.payment_method:
            self.payment_input.setText(self.expense.payment_method)
    
    def on_save(self):
        """Validate and save"""
        if self.amount_input.value() <= 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount.")
            return
        
        self.accept()
    
    def get_data(self):
        """Get form data"""
        time = self.time_input.time()
        time_obj = QTime(time.hour(), time.minute())
        
        return {
            'amount': self.amount_input.value(),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip() or None,
            'date': self.date_input.date().toPyDate(),
            'time': time_obj.toPyTime(),
            'payment_method': self.payment_input.text().strip() or None
        }
